from odoo import api, fields, models, _
from dateutil.relativedelta import relativedelta
from odoo.exceptions import UserError

class TrainingTicket(models.Model):
    _name = "training.ticket"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = "Training Ticket"

    def _get_default_stage_id(self):
        return self.env['training.stage'].search([], order='sequence', limit=1)

    name = fields.Char(string="Name", copy=False, tracking=True, default="New", readonly=True)
    ticket_name = fields.Char("Ticket Name")
    contract_id = fields.Many2one('contract.contract', string="Related Contract", tracking=True)
    date = fields.Datetime(string="Date", default=fields.Datetime.now(), tracking=True)
    training_type_id = fields.Many2one('training.type', string="Training Type", tracking=True)
    allowed_stage_ids = fields.Many2many(related="training_type_id.allowed_stage_ids")
    stage_id = fields.Many2one('training.stage',string="Status", copy=False,default=_get_default_stage_id,
    tracking=True,domain="[('id', 'in', allowed_stage_ids)]")
    expense_ids = fields.One2many('hr.expense.sheet', 'training_id', string='Expenses')
    attendee_ids = fields.One2many('training.attendees', 'training_id', string='Attendees')
    color = fields.Integer(string='Color Index')
    active = fields.Boolean(default=True)
    budget_ids = fields.One2many('budget.analytic', 'training_id', string='Budgets')
    letters_certificate_attachment_ids = fields.Many2many('ir.attachment', string="Letters & Certificates")
    budget_sheet_attachment_ids = fields.Many2many("ir.attachment", string="Budget Sheet", relation="rel_budget_sheet_training_document")
    partner_id = fields.Many2one('res.partner', string="Vendor")
    po_count =fields.Integer(string="PO Count", compute="_compute_po_count")
    analytic_account_id = fields.Many2one('account.analytic.account', string='Budget')
    attachment_ids = fields.Many2many("ir.attachment", string="Attachments", relation="rel_training_document")
    modality_id = fields.Many2one('contract.modality', string='Modality')
    training_location_id = fields.Many2one('training.location', string="Location",
                                       tracking=True)
    timeoff_deputy = fields.Many2one("res.users", compute="compute_timeoff_deputy", store=True)
    modality_users = fields.Many2many('res.users', compute="compute_timeoff_deputy", store=True)
    site_sector_id = fields.Many2one("site.sector", string="Site Sector")
    instructor_id = fields.Many2one('res.partner', string="Instructor")
    previous_abroad_trained = fields.Integer(string="No. of Prev. Abroad Trained")
    previous_locally_trained = fields.Integer(string="No. of Prev. Locally Trained")
    contract_id_1 = fields.Many2one('contract.contract', string="Latest Contract No.1")
    contract_id_2 = fields.Many2one('contract.contract', string="Latest Contract No.2")
    installed_base_quantity = fields.Integer(string="Installed Base Quantity")
    partner_ids = fields.Many2many('res.partner', string="Nominated Engineers")

    @api.depends('create_uid','modality_id')
    def compute_timeoff_deputy(self):
        for rec in self:
            rec.timeoff_deputy = rec.create_uid.employee_id.timeoff_deputy.user_id.id
            rec.modality_users = rec.modality_id.user_ids.ids

    def set_deputy_modality_users(self):
        training = self.env['training.ticket'].search([])
        for rec in training:
            rec.timeoff_deputy = rec.create_uid.employee_id.timeoff_deputy.user_id.id
            rec.modality_users = rec.modality_id.user_ids.ids
    
    @api.model
    def create(self, vals):
        if vals.get('name', _('New')) == _('New'):
            vals['name'] = self.env['ir.sequence'].next_by_code(
                'training.seq') or _('New')
            res = super(TrainingTicket, self).create(vals)
        if self.env.user not in self.env.ref("custom_training.group_training_administrator").users:
            for user in self.env.ref("custom_training.group_training_administrator").users:
                self.env['mail.activity'].sudo().create({
                    'display_name': 'Ticket',
                    'summary': 'Ticket Created',
                    'note': "A training ticket is created by the user '" +self.env.user.name + "'.",
                    'date_deadline': fields.datetime.now(),
                    'user_id': user.id,
                    'res_id': res.id,
                    'res_model_id': self.env['ir.model'].sudo().search(
                        [('model', '=', 'training.ticket')],
                        limit=1).id,
                    'activity_type_id': self.env.ref(
                        'custom_training.mail_activity_training_notify_user').id,
                })
        if vals.get('training_type_id'):
            training_type = self.env['training.type'].browse(vals.get('training_type_id'))
            if vals.get('contract_id'):
                contract = self.env['contract.contract'].browse(vals.get('contract_id')).name
            else:
                contract = 'False'
            if training_type:
                if training_type.activity_users_ids:
                    for user in training_type.activity_users_ids:
                        self.env['mail.activity'].sudo().create({
                            'display_name': 'Ticket',
                            'summary': 'Ticket Created',
                            'note': training_type.name  + " for contract " + contract +" requires your attention.",
                            'date_deadline': fields.datetime.now(),
                            'user_id': user.id,
                            'res_id': res.id,
                            'res_model_id': self.env['ir.model'].sudo().search(
                                [('model', '=', 'training.ticket')],
                                limit=1).id,
                            'activity_type_id': self.env.ref('custom_training.mail_activity_training_notify_user').id,
                        })
            letters_certificate_attachment_ids = res.mapped('letters_certificate_attachment_ids')
            budget_sheet_attachment_ids = res.mapped('budget_sheet_attachment_ids')
            attachment_ids = res.mapped('attachment_ids')
            letters_certificate_attachment_ids.write({
                'res_id': res.id,
            })
            budget_sheet_attachment_ids.write({
                'res_id': res.id,
            })
            attachment_ids.write({
                'res_id': res.id,
            })
        return res

    def write(self, vals):
        if vals.get('stage_id'):
            if self.activity_ids:
                self.activity_ids.action_done()
            new_stage_id = self.env["training.stage"].browse(vals.get('stage_id'))
            if self.training_type_id:
                if self.training_type_id.require_letters_certificate:
                    if new_stage_id.require_letters_certificate and not self.letters_certificate_attachment_ids:
                        raise UserError(_("You need to upload a Letters & Certificate before moving the task to this stage"))
            if self.stage_id:
                if new_stage_id:
                    if self.env.user.id not in self.stage_id.move_from_user_ids.ids:
                        raise UserError(
                            _("You don't have access from move the training ticket from this stage."))
                    if self.env.user.id not in new_stage_id.move_to_user_ids.ids:
                        raise UserError(
                            _("You don't have access to move the training ticket to this stage."))
            if new_stage_id.require_purchase_order:
                purchase_order = self.env['purchase.order'].search([('training_id', '=', self.id)])
                if not purchase_order:
                    po = self.env['purchase.order'].create({
                        'partner_id': self.partner_id.id,
                        'partner_ref': self.contract_id.name + "-" + self.name,
                        'training_id': self.id,
                    })
                    if po:
                        if new_stage_id.users_notified_po:
                            for user in new_stage_id.users_notified_po:
                                self.env['mail.activity'].sudo().create({
                                    'display_name': 'Ticket',
                                    'summary': 'Purchase Order Created',
                                    'note': "A new purchase order " +po.name + " is created for the training ticket " + self.name + ".",
                                    'date_deadline': fields.datetime.now(),
                                    'user_id': user.id,
                                    'res_id': po.id,
                                    'res_model_id': self.env[
                                        'ir.model'].search(
                                        [('model', '=', 'purchase.order')],
                                        limit=1).id,
                                    'activity_type_id': self.env.ref(
                                        'custom_training.mail_activity_purchase_order_create').id,
                                })

        if vals.get('training_type_id'):
            training_type = self.env['training.type'].browse(vals.get('training_type_id'))
            if vals.get('contract_id'):
                contract = self.env['contract.contract'].browse(vals.get('contract_id')).name
            elif self.contract_id:
                contract = self.contract_id.name
            else:
                contract = 'False'
            if training_type:
                if training_type.activity_users_ids:
                    for user in training_type.activity_users_ids:
                        self.env['mail.activity'].sudo().create({
                            'display_name': 'Ticket',
                            'summary': 'Ticket Created',
                            'note': training_type.name  + " for contract " + contract +" requires your attention.",
                            'date_deadline': fields.datetime.now(),
                            'user_id': user.id,
                            'res_id': self.id,
                            'res_model_id': self.env['ir.model'].sudo().search(
                                [('model', '=', 'training.ticket')],
                                limit=1).id,
                            'activity_type_id': self.env.ref('custom_training.mail_activity_training_notify_user').id,
                        })
        return super(TrainingTicket, self).write(vals)


    def action_send_due_date_reminder(self):
        users = self.env.ref("custom_training.group_training_officer").users
        days_before_due = self.env['ir.config_parameter'].sudo().get_param(
            'custom_training.days_to_remind')
        base_url = self.env['ir.config_parameter'].sudo().get_param(
            'web.base.url')
        action_id = self.env.ref(
            'custom_training.action_training_ticket').id
        for rec in self.env['training.ticket'].search([]):
            if rec.date:
                date_of_reminder = rec.date - relativedelta(days=int(days_before_due))
                if date_of_reminder.date() == fields.Date.today():
                    email_template = self.env.ref('custom_training.mail_template_training_date')
                    ctx = {
                        'email_to': ','.join([p.partner_id.email for p in users]),
                        'date': days_before_due,
                        'contract': rec.contract_id.name,
                        'url': '%s/web#id=%s&action=%s&model=training.ticket&view_type=form' % (
                            base_url, rec.id, action_id),
                        'training': rec.name,
                    }
                    email_template.with_context(ctx).send_mail(self.id,
                                                               force_send=True)
                    body = "Due date for the training <a href=" + '%s/web#id=%s&action=%s&model=training.ticket&view_type=form' % (
                            base_url, rec.id, action_id) + "><strong>"+ rec.name +"</strong></a> will be meet in " + days_before_due+ " days, for your actions."

                    self.env['mail.message'].create(
                        {
                            'message_type': 'notification',
                            'subtype_id': self.env.ref('mail.mt_note').id,
                            'res_id': rec.id,
                            'model': 'training.ticket',
                            'subject': _('Due date for training of contract %s') %rec.contract_id.name,
                            'body': body,
                            'partner_ids': [(4, p.partner_id.id) for p in users],
                        }
                    )

    @api.model
    def _read_group_stage_ids(self, stages, domain, order):
        return self.env['training.stage'].search([], order=order)

    def action_purchase_order(self):
        return {
            "type": "ir.actions.act_window",
            "res_model": "purchase.order",
            "views": [[False, "list"],
                      [False,"form"]],
            "domain": [("training_id", "=", self.id)],
            "context": dict(self._context, create=False),
            "name": "Purchase Order",
        }

    def _compute_po_count(self):
        po = self.env['purchase.order'].search([('training_id', '=', self.id)])
        if po:
            self.po_count = len(po)
        else:
            self.po_count = 0

    # @api.constrains('attachment_ids')
    # def onchange_attachment_ids(self):
    #     for attachment in self.attachment_ids:
    #         workspace = self.env['ir.attachment'].sudo().search([('name', '=', self.name)])
    #         if not workspace:
    #             parent_workspace_type = self.env['ir.attachment'].sudo().search([('name', '=', self.training_type_id.name)])
    #             if not parent_workspace_type:
    #                 parent_workspace = self.env['ir.attachment'].sudo().search([('name', '=', 'Training'), ('parent_folder_id', '=', False)])
    #                 if not parent_workspace:
    #                     parent_workspace = self.env['ir.attachment'].sudo().create({
    #                         'name': 'Training',
    #                         'group_ids': [(6, 0, [self.env.ref('custom_training.group_training_officer').id])],
    #                         'read_group_ids': [(6, 0, [self.env.ref('custom_training.group_training_officer').id])]
    #                     })
    #                 parent_workspace_type = self.env['ir.attachment'].sudo().create({
    #                     'name': self.training_type_id.name,
    #                     'parent_folder_id': parent_workspace.id,
    #                     'group_ids': [(6, 0, [self.env.ref('custom_training.group_training_officer').id])],
    #                     'read_group_ids': [(6, 0, [self.env.ref('custom_training.group_training_officer').id])]
    #                 })
    #             workspace = self.env['ir.attachment'].sudo().create({
    #                 'name':self.name,
    #                 'parent_folder_id': parent_workspace_type.id,
    #                 'group_ids': [(6, 0, [self.env.ref('custom_training.group_training_officer').id])],
    #                 'read_group_ids': [(6, 0, [self.env.ref('custom_training.group_training_officer').id])]
    #             })
    #         self.env['ir.attachment'].sudo().create({
    #             'name': attachment.name,
    #             'datas': attachment.datas,
    #             'folder_id': workspace.id
    #         })

    def get_filter_records(self, attendee):
        tickets = self.env['training.attendees'].search(
            [('attendee_id.name', 'ilike', attendee)]).mapped(
            'training_id.id')
        return list(set(tickets))
