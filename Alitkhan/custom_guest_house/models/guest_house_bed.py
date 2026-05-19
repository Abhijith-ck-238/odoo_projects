from odoo import models, fields, api, _


class GuesthouseBed(models.Model):
    _name = 'guest.house.bed'
    _description = 'Guest House Bed'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string="Bed Number", readonly=True, copy=False, default="New")
    is_reserved = fields.Boolean(string="Is Reserved", readonly=True, compute="compute_is_reserved")
    reserve = fields.Boolean()
    guest_house_id = fields.Many2one("guest.house", string="Guest House", required=True)
    province_id = fields.Many2one('contract.province', related='guest_house_id.province_id')
    reservation_ids = fields.One2many('bed.reservation', 'bed_id', string="Reservations",
                                      domain=[('state','!=', 'cancelled'),('date_to', '>=', fields.Datetime.now())])
    current_reservation_ids = fields.Many2many('bed.reservation', compute="_compute_current_reservation_ids", string="Reservation")

    @api.depends('reservation_ids')
    def _compute_current_reservation_ids(self):
        for rec in self:
            rec.current_reservation_ids = False
            for reservation in rec.reservation_ids:
                if fields.Datetime.now() >= reservation.date_from and fields.Datetime.now() <= reservation.date_to:
                    rec.write({'current_reservation_ids': [(4, reservation.id)]})

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', _('New')) == _('New'):
                vals['name'] = self.env['ir.sequence'].next_by_code('guest.house.bed.seq') or _('New')
        return super(GuesthouseBed, self).create(vals_list)

    def action_reserve_bed(self):
        return {
            'name': "Reservation",
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'reservation.wizard',
            'view_id': self.env.ref(
                'custom_guest_house.bed_reservation_view_wizard').id,
            'target': 'new',
        }

    @api.depends('reservation_ids', 'reservation_ids.date_from',
                 'reservation_ids.date_to')
    def compute_is_reserved(self):
        current_datetime = fields.Datetime.now()
        for rec in self:
            rec.is_reserved = False
            rec.reserve = False
            for reservation in rec.reservation_ids.filtered(
                    lambda r: r.state != 'cancelled'):
                if current_datetime >= reservation.date_from and current_datetime <= reservation.date_to:
                    rec.is_reserved = True
                    rec.reserve = True
                    break  # Exit loop once a valid reservation is found
