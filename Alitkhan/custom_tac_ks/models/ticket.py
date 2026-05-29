from odoo import api, fields, models, _
import datetime
from dateutil.relativedelta import relativedelta

class TacKsTicket(models.Model):
    _name = "tac.ks.ticket"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = "TAC KS Ticket"

    def _get_default_stage_id(self):
        return self.env['ticket.stage'].search([], order='sequence', limit=1)

    name = fields.Char(string="Task Description", tracking=True)
    stage_id = fields.Many2one('ticket.stage',string="Stage", copy=False,
                               default=_get_default_stage_id, group_expand='_read_group_stage_ids', tracking=True, store=True)
    user_ids = fields.Many2many('res.users', string='Assignees', domain=lambda self: [(
                                  'groups_id', 'in', self.env.ref(
                                      'custom_tac_ks.group_tac_ks_user').id)])
    partner_id = fields.Many2one('res.partner', string='Customer')
    product_id = fields.Many2one('product.product', string='Product')
    serial_number_id = fields.Many2one('serial.number', string='Serial Number')
    notes = fields.Text(string="Notes", tracking=True)
    work_done = fields.Char(string="Work Done")
    ticket_type_id = fields.Many2one('ticket.type', string='Ticket Type')
    color = fields.Integer(string='Color Index')
    active = fields.Boolean(default=True)
    currency_id = fields.Many2one(
        'res.currency', 'Currency', compute='_compute_currency_id', store=True)
    company_id = fields.Many2one('res.company', string='Company',
                                 required=True,
                                 default=lambda self: self.env.company)
    offer_currency_id = fields.Many2one('res.currency', string='Offer Cost Currency')
    vendor_currency_id = fields.Many2one('res.currency', string='Vendor Cost Currency')
    offer_cost = fields.Monetary(string="Offer Cost")
    vendor_cost = fields.Monetary(string='Vendor Cost', currency_field='currency_id')
    backup_installed = fields.Boolean(string='Backup Installed')
    attachment_ids = fields.Many2many('ir.attachment',string="Attachments")
    start_date = fields.Date()
    end_date = fields.Date()
    date_last_stage_update = fields.Datetime(string='Last Stage Update',
                                             index=True)
    product_line_ids = fields.One2many("component.product", "ticket_id", string='Technical Awareness')


    @api.depends('company_id')
    def _compute_currency_id(self):
        main_company = self.env['res.company']._get_main_company()
        for template in self:
            template.currency_id = template.company_id.sudo().currency_id.id or main_company.currency_id.id



    @api.model
    def _read_group_stage_ids(self, stages, domain, order=None):
        return self.env['ticket.stage'].search([], order=order)

    @api.model
    def create(self, vals):
        res = super(TacKsTicket, self).create(vals)
        attachment_ids = res.mapped('attachment_ids')
        attachment_ids.write({
            'res_id': res.id,
        })
        user_ids_data = vals.get('user_ids', [])
        partner_id = vals.get('partner_id')
        customer_name = self.env['res.partner'].browse(
            partner_id).name if partner_id else 'Unknown'

        user_ids = []

        for cmd in user_ids_data:
            if cmd[0] == 6:
                user_ids.extend(cmd[2])
            elif cmd[0] == 4:
                user_ids.append(cmd[1])

        if user_ids:
            model_id = self.env['ir.model'].sudo()._get('tac.ks.ticket').id
            for uid in user_ids:
                self.env['mail.activity'].sudo().create({
                    'activity_type_id': 4,
                    'summary': 'Ticket Created',
                    'note': f"You have been assigned a task related to '{customer_name}'.",
                    'user_id': uid,
                    'res_id': res.id,
                    'res_model_id': model_id,
                    'date_deadline': fields.Date.today(),
                })

        return res

    def write(self, vals):
        res = super(TacKsTicket, self).write(vals)
        activities = self.activity_ids.ids
        if vals.get('stage_id'):
            self.date_last_stage_update = fields.Datetime.now()
            sequence = self.env['ticket.stage'].browse(vals.get('stage_id')).sequence
            if sequence == 1:
                self.env['mail.activity'].browse(activities).action_done()
        return res

    def get_filter_records(self, serial_number):
        awareness = self.env['component.product'].search(
            [('serial_number_id.name', 'ilike', serial_number)]).mapped('ticket_id.id')
        return list(set(awareness))

    def action_send_notification(self):
        users = self.env.ref("custom_tac_ks.group_tac_ks_user").users
        administrators = self.env.ref("custom_tac_ks.group_tac_ks_administrator").users
        for rec in users:
            current_time = datetime.datetime.strftime(
                fields.Datetime.context_timestamp(self,
                                                  datetime.datetime.now()),
                "%Y-%m-%d %H:%M:%S")
            date_format = '%Y-%m-%d %H:%M:%S'
            date_obj = datetime.datetime.strptime(current_time, date_format)
            previous_date = date_obj - relativedelta(hours=24)
            tickets = self.env['tac.ks.ticket'].search(
                [('create_date', '>=', previous_date),
                 ('create_uid', '=', rec.id)])
            if not tickets:
                message = self.env['mail.message'].create(
                    {
                        'message_type': 'notification',
                        'subtype_id': self.env.ref('mail.mt_note').id,
                        'model': 'tac.ks.ticket',
                        'subject': 'No ticket is created by the user %s for the past 24 hours' % rec.name,
                        'body': _(
                            'No Tac KS ticket is created by the user %s for the past 24 hours.') % rec.name,
                        'partner_ids': [(4, p.partner_id.id) for p in
                                        administrators],
                        'notification_ids': [(0, 0, {
                            'res_partner_id': p.partner_id.id,
                            'notification_type': 'inbox',
                            'notification_status': 'sent'
                        }) for p in administrators],

                    }
                )
