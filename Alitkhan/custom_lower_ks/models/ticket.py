import datetime
from odoo import api, fields, models, _
from dateutil.relativedelta import relativedelta
import logging

_logger = logging.getLogger(__name__)


class LowerKsTicket(models.Model):
    _name = "lower.ks.ticket"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = "Lower KS Ticket"

    AVAILABLE_PRIORITIES = [
        ('0', 'Normal'),
        ('1', 'Good'),
        ('2', 'Very Good'),
        ('3', 'Excellent')
    ]

    def _get_default_stage_id(self):
        return self.env['lower.ks.ticket.stage'].search([], order='sequence',
                                                        limit=1)

    name = fields.Char(string="Task Description", tracking=True)
    stage_id = fields.Many2one('lower.ks.ticket.stage', string="Stage",
                               copy=False, group_expand='_read_group_stage_ids',
                               default=_get_default_stage_id, tracking=True,
                               store=True)

    user_ids = fields.Many2many('res.users', string='Assignees',
                                domain=lambda self: [(
                                    'groups_id', 'in', self.env.ref(
                                        'custom_lower_ks.group_lower_ks_user').id)])
    partner_id = fields.Many2one('res.partner', string='Customer')
    notes = fields.Text(string="Notes", tracking=True)
    work_done = fields.Char(string="Work Done")
    ticket_type_id = fields.Many2one('lower.ks.ticket.type',
                                     string='Ticket Type')
    color = fields.Integer(string='Color Index')
    active = fields.Boolean(default=True)
    currency_id = fields.Many2one(
        'res.currency', 'Currency', compute='_compute_currency_id', store=True)
    company_id = fields.Many2one('res.company', string='Company',
                                 required=True,
                                 default=lambda self: self.env.company)
    attachment_ids = fields.Many2many('ir.attachment', string="Attachments")
    start_date = fields.Datetime()
    # convert datetime field to date field
    start_ddate = fields.Date()
    end_date = fields.Datetime()
    end_ddate = fields.Date()
    date_last_stage_update = fields.Datetime(string='Last Stage Update',
                                             index=True)
    work_sector_id = fields.Many2one("lower.ks.work.sector",
                                     string="Work Sector")
    account_id = fields.Many2one('lower.ks.account', string="Account")
    source_id = fields.Many2one('lower.ks.source', string="Source")
    province_id = fields.Many2one('lower.ks.province', string='Province')
    speciality_id = fields.Many2many('lower.ks.speciality', string='Speciality')
    priority = fields.Selection(AVAILABLE_PRIORITIES, "Priority")
    # will be true after server action is done to convert date time to date of start_date and end_date field works
    action_done = fields.Boolean("Server action done")

    @api.depends('company_id')
    def _compute_currency_id(self):
        main_company = self.env['res.company']._get_main_company()
        for template in self:
            template.currency_id = template.company_id.sudo().currency_id.id or main_company.currency_id.id

    @api.model
    def _read_group_stage_ids(self, stages, domain):
        return self.env['lower.ks.ticket.stage'].search([])

    @api.model
    def create(self, vals):
        res = super(LowerKsTicket, self).create(vals)
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
            model_id = self.env['ir.model'].sudo()._get('lower.ks.ticket').id
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
        res = super(LowerKsTicket, self).write(vals)
        activities = self.activity_ids.ids
        if vals.get('stage_id'):
            self.date_last_stage_update = fields.Datetime.now()
            sequence = self.env['lower.ks.ticket.stage'].browse(
                vals.get('stage_id')).sequence
            if sequence == 1:
                self.env['mail.activity'].browse(activities).action_done()
        return res

    def action_move_datetime_date(self):
        for rec in self:
            updates = {'action_done': True}
            if rec.start_date:
                updates['start_ddate'] = rec.start_date.date()
            if rec.end_date:
                updates['end_ddate'] = rec.end_date.date()
            rec.write(updates)

    def action_send_notification(self):
        users = self.env.ref("custom_lower_ks.group_lower_ks_user").users
        administrators = self.env.ref(
            "custom_lower_ks.group_lower_ks_administrator").users
        for rec in users:
            current_time = datetime.datetime.strftime(
                fields.Datetime.context_timestamp(self,
                                                  datetime.datetime.now()),
                "%Y-%m-%d %H:%M:%S")
            date_format = '%Y-%m-%d %H:%M:%S'
            date_obj = datetime.datetime.strptime(current_time, date_format)
            previous_date = date_obj - relativedelta(hours=24)
            tickets = self.env['lower.ks.ticket'].search(
                [('create_date', '>=', previous_date),
                 ('create_uid', '=', rec.id)])
            if not tickets:
                message = self.env['mail.message'].create(
                    {
                        'message_type': 'notification',
                        'subtype_id': self.env.ref('mail.mt_note').id,
                        'model': 'lower.ks.ticket',
                        'subject': 'No ticket is created by the user %s for the past 24 hours' % rec.name,
                        'body': _(
                            'No Lower KS ticket is created by the user %s for the past 24 hours.') % rec.name,
                        'partner_ids': [(4, p.partner_id.id) for p in
                                        administrators],
                        'notification_ids': [(0, 0, {
                            'res_partner_id': p.partner_id.id,
                            'notification_type': 'inbox',
                            'notification_status': 'sent'
                        }) for p in administrators],

                    }
                )

    @api.model
    def fix_helpdesk_attachment_res_id(self):
        contracts = self.search([])
        Attachment = self.env['ir.attachment']
        count = 0
        for contract in contracts:
            attachments = contract.attachment_ids

            attachments_to_fix = attachments.filtered(
                lambda att: not att.res_id or att.res_id == 0
            )
            count += len(attachments_to_fix)

            if attachments_to_fix:
                attachments_to_fix.write({
                    'res_id': contract.id,
                    'res_model': contract._name,
                })
            _logger.info("Fixed %s helpdesk attachments", count)

