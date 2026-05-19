from odoo import models, fields, api, _
import pytz
from odoo.exceptions import UserError
import logging

_logger = logging.getLogger(__name__)



class BedReservation(models.Model):
    _name = "bed.reservation"
    _description = "Bed Reservation"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'combination'

    name = fields.Char(string="Reservation Number", readonly=True, copy=False,
                       default="New")
    employee_id = fields.Many2one('hr.employee', string="Employee", required=True)
    arabic_name = fields.Char(string="Arabic Name", related="employee_id.arabic_name")
    department_id = fields.Many2one('hr.department', string="Department", related="employee_id.department_id")
    division_id = fields.Many2one('division.division', string="Division", related="employee_id.new_divisions")
    guest_house_id = fields.Many2one('guest.house', string="Guest House", required=True)
    bed_ids = fields.Many2many('guest.house.bed', compute="_compute_bed_ids", store=True,
                               relation='reservation_bed_rel',column1="reservation_id", column2="bed_id")
    bed_id = fields.Many2one('guest.house.bed', string="Bed", domain="[('id', 'in', bed_ids)]",required=True)
    date_from = fields.Datetime(string="From Date",required=True)
    date_to = fields.Datetime(string="To Date",required=True)
    user_id = fields.Many2one('res.users', related="employee_id.user_id")
    state = fields.Selection(selection=[('reserved', 'Reserved'),
                                        ('cancelled', 'Cancelled')], default="reserved")
    combination = fields.Char(string='Combination',
                              compute='_compute_fields_combination')
    active = fields.Boolean(default=True)

    @api.depends('guest_house_id')
    def _compute_bed_ids(self):
        for rec in self:
            rec.bed_ids = False
            rec.write({'bed_ids': [(4, x.id)
                                       for x in rec.guest_house_id.bed_ids]})

    @api.depends('date_from', 'date_to')
    def _compute_fields_combination(self):
        for rec in self:
            if not rec.date_from or not rec.date_to:
                rec.combination = ""
                continue

            tz = self.env.user.tz or 'UTC'
            att_tz = pytz.timezone(tz)

            try:
                # Convert date_from
                date_from = rec.date_from.replace(tzinfo=pytz.utc).astimezone(
                    att_tz)
                from_date_formatted = date_from.strftime('%d/%m %I:%M %p')

                # Convert date_to
                date_to = rec.date_to.replace(tzinfo=pytz.utc).astimezone(
                    att_tz)
                to_date_formatted = date_to.strftime('%d/%m %I:%M %p')

                rec.combination = f"{from_date_formatted} - {to_date_formatted}"
            except Exception as e:
                rec.combination = "Invalid Date"
                _logger.error(f"Error computing fields combination: {e}")

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            # Assign sequence number if name is 'New'
            if vals.get('name', _('New')) == _('New'):
                vals['name'] = self.env['ir.sequence'].next_by_code(
                    'reservation.seq') or _('New')

            date_from = vals.get('date_from')
            date_to = vals.get('date_to')

            # Safety check: Ensure both dates are provided
            if not date_from or not date_to:
                raise UserError(_('Both From Date and To Date are required.'))

            if date_to <= date_from:
                raise UserError(
                    _('The To Date must be after the From Date.'))

            # Check for overlapping reservations
            reservations = self.env['bed.reservation'].search([
                ('bed_id', '=', vals.get('bed_id')),
                ('date_to', '>=', fields.Datetime.now()),
                ('date_from', '<', date_to),
                ('date_to', '>', date_from),
                ('state', '!=', 'cancelled')
            ], order='date_from asc')

            if reservations:
                reserved_dates = []
                tz = self.env.user.tz or 'UTC'
                att_tz = pytz.timezone(tz)

                for rec in reservations:
                    res_from = fields.Datetime.from_string(
                        rec.date_from).replace(tzinfo=pytz.utc).astimezone(
                        att_tz)
                    res_to = fields.Datetime.from_string(rec.date_to).replace(
                        tzinfo=pytz.utc).astimezone(att_tz)
                    reserved_dates.append(
                        f"{res_from.strftime('%Y-%m-%d %I:%M %p')} to {res_to.strftime('%Y-%m-%d %I:%M %p')}")

                raise UserError(
                    _('The bed is already reserved for: ') + ", ".join(
                        reserved_dates))

        # Create reservation records
        res = super(BedReservation, self).create(vals_list)

        # Send notifications
        for reservation in res:
            tz = self.env.user.tz or 'UTC'
            att_tz = pytz.timezone(tz)

            date_from = fields.Datetime.from_string(
                reservation.date_from).replace(tzinfo=pytz.utc).astimezone(
                att_tz)
            date_to = fields.Datetime.from_string(reservation.date_to).replace(
                tzinfo=pytz.utc).astimezone(att_tz)

            body = _("Bed {} reserved from {} to {} by employee {}.").format(
                reservation.bed_id.name,
                date_from.strftime('%Y-%m-%d %I:%M %p'),
                date_to.strftime('%Y-%m-%d %I:%M %p'),
                reservation.employee_id.name
            )

            self.env['mail.message'].create({
                'message_type': 'comment',
                'subtype_id': self.env.ref('mail.mt_note').id,
                'res_id': reservation.id,
                'model': 'bed.reservation',
                'subject': _('Bed Reserved'),
                'body': body,
                'partner_ids': [(4, user.partner_id.id) for user in
                                reservation.guest_house_id.user_ids],
                'notification_ids': [(0, 0, {
                    'res_partner_id': user.partner_id.id,
                    'notification_type': 'inbox',
                }) for user in reservation.guest_house_id.user_ids],
            })

            for user in reservation.guest_house_id.user_ids:
                self.env['mail.activity'].sudo().create({
                    'display_name': 'Bed Reserved',
                    'summary': 'Bed Reserved',
                    'note': body,
                    'date_deadline': fields.Datetime.now(),
                    'user_id': user.id,
                    'res_id': reservation.id,
                    'res_model_id': self.env['ir.model'].sudo().search(
                        [('model', '=', 'bed.reservation')], limit=1).id,
                    'activity_type_id': self.env.ref(
                        'custom_guest_house.mail_activity_bed_reserved').id,
                })

        return res
    def write(self, vals):
        reservations = self.env['bed.reservation'].search([
            ('bed_id', '=', vals.get('bed_id', self.bed_id.id)),
            ('date_to', '>=', fields.Datetime.now()),
            ('date_from', '<', vals.get('date_to', self.date_to)),
            ('date_to', '>', vals.get('date_from', self.date_from)),
            ('state', '!=', 'cancelled'),
            ('id', '!=', self.id)], order='date_from asc')

        if reservations:
            reserved_dates = []
            tz = self.env.user.tz or 'UTC'
            att_tz = pytz.timezone(tz)

            for rec in reservations:
                date_from = rec.date_from.astimezone(att_tz)
                date_to = rec.date_to.astimezone(att_tz)
                reserved_dates.append(
                    f"{date_from.strftime('%Y-%m-%d %I:%M %p')} to {date_to.strftime('%Y-%m-%d %I:%M %p')}"
                )

            raise UserError(_('The bed is already reserved for: ') + ", ".join(
                reserved_dates))

        return super(BedReservation, self).write(vals)

    def action_cancel_reservation(self):
        self.write({'state': 'cancelled'})
        tz = self.env.user.tz or 'UTC'
        att_tz = pytz.timezone(tz)

        try:
            date_from = fields.Datetime.from_string(self.date_from).replace(
                tzinfo=pytz.utc).astimezone(att_tz)
            date_to = fields.Datetime.from_string(self.date_to).replace(
                tzinfo=pytz.utc).astimezone(att_tz)
        except Exception as e:
            raise UserError(_('Error in date conversion: %s') % str(e))

        from_date_formatted = date_from.strftime('%Y-%m-%d %I:%M:%S %p')
        to_date_formatted = date_to.strftime('%Y-%m-%d %I:%M:%S %p')

        body = _(
            f"Reservation {self.name} for the bed {self.bed_id.name} from {from_date_formatted} to {to_date_formatted} by the employee {self.employee_id.name} is cancelled.")

        self.env['mail.message'].create({
            'message_type': 'comment',
            'subtype_id': self.env.ref('mail.mt_note').id,
            'res_id': self.id,
            'model': 'bed.reservation',
            'subject': _('Reservation Cancelled'),
            'body': body,
            'partner_ids': [(4, p.partner_id.id) for p in
                            self.guest_house_id.user_ids],
            'notification_ids': [(0, 0, {'res_partner_id': p.partner_id.id,
                                         'notification_type': 'inbox'}) for p in
                                 self.guest_house_id.user_ids],
        })

        self.activity_ids.action_done()
        for user in self.guest_house_id.user_ids:
            self.env['mail.activity'].sudo().create({
                'display_name': 'Reservation Cancelled',
                'summary': 'Reservation Cancelled',
                'note': body,
                'date_deadline': fields.Datetime.now(),
                'user_id': int(user.id),
                'res_id': self.id,
                'res_model_id': self.env['ir.model'].sudo().search(
                    [('model', '=', 'bed.reservation')], limit=1).id,
                'activity_type_id': self.env.ref(
                    'custom_guest_house.mail_activity_reservation_cancelled').id,
            })
