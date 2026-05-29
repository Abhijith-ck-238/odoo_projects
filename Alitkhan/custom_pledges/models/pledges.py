import datetime
from datetime import timedelta
from odoo import models, fields, _, api

from odoo.exceptions import UserError


class CustomPledges(models.Model):
    """ Pledge """
    _name = 'pledge.pledge'
    _inherit = ['pledge.pledge','mail.thread','mail.activity.mixin']

    def _get_default_stage_id(self):
        return self.env['pledge.stage'].search([('sequence', '=', 0)], limit=1)

    active = fields.Boolean(default=True)
    deadline_ids = fields.One2many('alert.deadline', 'pledge_id',
                                   string="Deadlines")
    amendment_ids = fields.One2many('amendment.amendment', 'pledge_id')
    count_pending_amendments = fields.Integer(string="Pending Amendments",
                                              compute='compute_count_pending_amendments',
                                              search='search_amendments',tracking=True, store=True)
    payment_installation_ids = fields.One2many("payment.installation",
                                               "pledge_id",
                                               string="Payment Installation")
    paid_amount = fields.Monetary(string="Paid Amount",
                                  compute='compute_paid_amount', readonly=False,
                                  store=True, tracking=True)
    lc_type = fields.Selection(
        [('irrevocable', 'Irrevocable'), ('confirmed', 'Confirmed'),
         ('transferable', 'Transferable'), ('N/A', 'N/A'),
         ('Irrevocable and Confirmed', 'Irrevocable and Confirmed'),
         ('Irrevocable and Transferable', 'Irrevocable and Transferable')],
        string="Letter of Credit Type",tracking=True)  # if lc, what lc type
    date_of_extension = fields.Date(string="Date of Extension", tracking=True)
    contract_type = fields.Selection(selection=[('supplying_and_maintenance', 'Supplying & Maintenance'),
                                                ('maintenance', 'Maintenance'),
                                                ('supplying', 'Supplying'),
                                                ('3rd_party', '3rd Party'),
                                                ('demo', 'Demo'),
                                                ('n.a', 'N.A'),
                                                ('other', 'Other'),
                                                ('installation_only', 'Installation Only')], string="Contract Type", tracking=True)
    lc_type_id = fields.Many2one('lc.type', string="L/C Type",tracking=True)
    color = fields.Integer()
    stage_id = fields.Many2one('pledge.stage', string="Status", copy=False,
                               default=_get_default_stage_id,
                               group_expand='_read_group_stage_ids',
                               tracking=True, store=True)
    currency_rate = fields.Float(string="Currency Rate",compute='_compute_currency_rate', compute_sudo=True, store=True, digits=(12, 6), readonly=True)

    @api.depends('currency_id')
    def _compute_currency_rate(self):
        for order in self:
            order.currency_rate = order.currency_id.rate or 1.0

    is_partner_id_edit = fields.Boolean(compute="compute_is_editable")
    partner_id = fields.Many2one("res.partner", string="Partner/Customer", required=True, readonly=False, tracking=True)
    is_lca_type_edit = fields.Boolean(compute="compute_is_editable")
    lca_type = fields.Selection(
        [('bid bond', 'Bid Bond'), ('performance bond', 'Performance Bond'),
         ('letter of credit', 'Letter of Credit')],
        string="Pledge Type", tracking=True)
    is_related_contract_edit = fields.Boolean(compute="compute_is_editable")
    related_contract = fields.Many2one("contract.contract",
                                       string="Related Contract", tracking=True)
    is_bid_ref_edit = fields.Boolean(compute="compute_is_editable")
    bid_ref = fields.Char(string="Bid Reference",tracking=True)
    is_lc_type_edit = fields.Boolean(compute="compute_is_editable")
    is_payment_method_edit = fields.Boolean(compute="compute_is_editable")
    payment_method = fields.Char(string="Payment Method",tracking=True)
    is_contract_type_edit = fields.Boolean(compute="compute_is_editable")
    is_count_pending_amendments_edit = fields.Boolean(compute="compute_is_editable")
    is_issuing_bank_name_edit = fields.Boolean(compute="compute_is_editable")
    issuing_bank_name = fields.Many2one("pledge.bank", required=True, tracking=True)
    is_benefeciary_bank_edit = fields.Boolean(compute="compute_is_editable")
    benefeciary_bank = fields.Many2one("pledge.bank",
                                       string="Benefeciary Bank", tracking=True)
    is_currency_id_edit = fields.Boolean(compute="compute_is_editable")
    currency_id = fields.Many2one('res.currency', string='Currency',tracking=True)
    is_amount_edit = fields.Boolean(compute="compute_is_editable")
    amount = fields.Monetary(string="Amount", tracking=True)
    is_x_studio_amount_coverage_edit = fields.Boolean(compute="compute_is_editable")
    is_paid_amount_edit = fields.Boolean(compute="compute_is_editable")
    is_parent_pledge_edit = fields.Boolean(compute="compute_is_editable")
    parent_pledge = fields.Many2one('pledge.pledge', string="Parent Pledge",tracking=True)
    is_issuing_bank_ref_edit = fields.Boolean(compute="compute_is_editable")
    issuing_bank_ref = fields.Char(string="LC Number",tracking=True)
    is_lc_type_id_edit = fields.Boolean(compute="compute_is_editable")
    is_attachment_ids_edit = fields.Boolean(compute="compute_is_editable")
    attachment_ids = fields.Many2many('ir.attachment', string='Attachments',tracking=True)
    is_x_studio_opining_date_edit = fields.Boolean(compute="compute_is_editable")
    is_acceptance_date_edit = fields.Boolean(compute="compute_is_editable")
    acceptance_date = fields.Date(string="Acceptance date",tracking=True)
    is_x_studio_expire_date_edit = fields.Boolean(compute="compute_is_editable")
    is_date_of_extension_edit = fields.Boolean(compute="compute_is_editable")
    is_notes_edit = fields.Boolean(compute="compute_is_editable")
    notes = fields.Text(tracking=True)
    is_validity_lines_edit = fields.Boolean(compute="compute_is_editable")
    is_expense_lines_edit = fields.Boolean(compute="compute_is_editable")
    is_deadline_ids_edit = fields.Boolean(compute="compute_is_editable")
    is_amendment_ids_edit = fields.Boolean(compute="compute_is_editable")
    is_payment_installation_ids_edit = fields.Boolean(compute="compute_is_editable")
    is_clearance_amount_edit = fields.Boolean(compute="compute_is_editable")
    is_clearance_attachments_edit = fields.Boolean(compute="compute_is_editable")
    clearance_amount = fields.Integer(string="Clearance Amount",tracking=True)
    clearance_attachement = fields.Binary(string='Attachments')
    x_studio_amount_coverage = fields.Float(string="Amount Coverage",tracking=True)
    x_studio_opining_date = fields.Date(string="Opining Date",tracking=True)
    x_studio_expire_date = fields.Date(string="Expire Date", tracking=True)

    def action_set_pledge_stage(self):
        pledges = self.env['pledge.pledge'].search([("stage_id", "=", False)])
        for rec in pledges:
            stage_id = self.env['pledge.stage'].search([('sequence', '=', 0)], limit=1).id
            rec.write({
                'stage_id' : stage_id
            })

    @api.model
    def create(self, vals):
        res = super(CustomPledges, self).create(vals)
        attachment_ids = res.mapped('attachment_ids')
        attachment_ids.write({
            'res_id': res.id,
        })
        return res

    def compute_is_editable(self):
        for rec in self:
            partner_field_id = self.env.ref('pledge_assets.field_pledge_pledge__partner_id').id
            partner_access_user = self.env['field.access'].search([('field_id','=',partner_field_id)]).user_ids.ids
            if self.env.user.id in partner_access_user:
                rec.is_partner_id_edit = True
            else:
                rec.is_partner_id_edit = False
            lca_type_field_id = self.env.ref('pledge_assets.field_pledge_pledge__lca_type').id
            lca_type_access_user = self.env['field.access'].search([('field_id', '=', lca_type_field_id)]).user_ids.ids
            if self.env.user.id in lca_type_access_user:
                rec.is_lca_type_edit = True
            else:
                rec.is_lca_type_edit = False
            related_contract_field_id = self.env.ref('pledge_assets.field_pledge_pledge__related_contract').id
            related_contract_access_user = self.env['field.access'].search([('field_id', '=', related_contract_field_id)]).user_ids.ids
            if self.env.user.id in related_contract_access_user:
                rec.is_related_contract_edit = True
            else:
                rec.is_related_contract_edit = False
            bid_ref_field_id = self.env.ref('pledge_assets.field_pledge_pledge__bid_ref').id
            bid_ref_access_user = self.env['field.access'].search([('field_id', '=', bid_ref_field_id)]).user_ids.ids
            if self.env.user.id in bid_ref_access_user:
                rec.is_bid_ref_edit = True
            else:
                rec.is_bid_ref_edit = False
            lc_type_field_id = self.env.ref('pledge_assets.field_pledge_pledge__lc_type').id
            lc_type_access_user = self.env['field.access'].search([('field_id', '=', lc_type_field_id)]).user_ids.ids
            if self.env.user.id in lc_type_access_user:
                rec.is_lc_type_edit = True
            else:
                rec.is_lc_type_edit = False
            payment_method_field_id = self.env.ref('pledge_assets.field_pledge_pledge__payment_method').id
            payment_method_access_user = self.env['field.access'].search([('field_id', '=', payment_method_field_id)]).user_ids.ids
            if self.env.user.id in payment_method_access_user:
                rec.is_payment_method_edit = True
            else:
                rec.is_payment_method_edit = False
            contract_type_field_id = self.env.ref('custom_pledges.field_pledge_pledge__contract_type').id
            contract_type_access_user = self.env['field.access'].search([('field_id', '=', contract_type_field_id)]).user_ids.ids
            if self.env.user.id in contract_type_access_user:
                rec.is_contract_type_edit = True
            else:
                rec.is_contract_type_edit = False
            count_pending_amendments_field_id = self.env.ref('custom_pledges.field_pledge_pledge__count_pending_amendments').id
            count_pending_amendments_access_user = self.env['field.access'].search([('field_id', '=', count_pending_amendments_field_id)]).user_ids.ids
            if self.env.user.id in count_pending_amendments_access_user:
                rec.is_count_pending_amendments_edit = True
            else:
                rec.is_count_pending_amendments_edit = False
            issuing_bank_name_field_id = self.env.ref('pledge_assets.field_pledge_pledge__issuing_bank_name').id
            issuing_bank_name_access_user = self.env['field.access'].search([('field_id', '=',issuing_bank_name_field_id)]).user_ids.ids
            if self.env.user.id in issuing_bank_name_access_user:
                rec.is_issuing_bank_name_edit = True
            else:
                rec.is_issuing_bank_name_edit = False
            benefeciary_bank_field_id = self.env.ref('pledge_assets.field_pledge_pledge__benefeciary_bank').id
            benefeciary_bank_access_user = self.env['field.access'].search([('field_id', '=', benefeciary_bank_field_id)]).user_ids.ids
            if self.env.user.id in benefeciary_bank_access_user:
                rec.is_benefeciary_bank_edit = True
            else:
                rec.is_benefeciary_bank_edit = False
            currency_id_field_id = self.env.ref('pledge_assets.field_pledge_pledge__currency_id').id
            currency_id_access_user = self.env['field.access'].search([('field_id', '=', currency_id_field_id)]).user_ids.ids
            if self.env.user.id in currency_id_access_user:
                rec.is_currency_id_edit = True
            else:
                rec.is_currency_id_edit = False
            amount_field_id = self.env.ref('pledge_assets.field_pledge_pledge__amount').id
            amount_access_user = self.env['field.access'].search([('field_id', '=', amount_field_id)]).user_ids.ids
            if self.env.user.id in amount_access_user:
                rec.is_amount_edit = True
            else:
                rec.is_amount_edit = False
            x_studio_amount_coverage_field_id = self.env.ref('studio_customization.new_decimal_pledge_p_4bf34ed8-909d-494b-bfc7-981e68f3b994').id
            x_studio_amount_coverage_access_user = self.env['field.access'].search([('field_id', '=', x_studio_amount_coverage_field_id)]).user_ids.ids
            if self.env.user.id in x_studio_amount_coverage_access_user:
                rec.is_x_studio_amount_coverage_edit = True
            else:
                rec.is_x_studio_amount_coverage_edit = False
            paid_amount_field_id = self.env.ref('pledge_assets.field_pledge_pledge__paid_amount').id
            paid_amount_access_user = self.env['field.access'].search([('field_id', '=',paid_amount_field_id)]).user_ids.ids
            if self.env.user.id in paid_amount_access_user:
                rec.is_paid_amount_edit = True
            else:
                rec.is_paid_amount_edit = False
            parent_pledge_field_id = self.env.ref('pledge_assets.field_pledge_pledge__parent_pledge').id
            parent_pledge_access_user = self.env['field.access'].search([('field_id', '=', parent_pledge_field_id)]).user_ids.ids
            if self.env.user.id in parent_pledge_access_user:
                rec.is_parent_pledge_edit = True
            else:
                rec.is_parent_pledge_edit = False
            issuing_bank_ref_field_id = self.env.ref('pledge_assets.field_pledge_pledge__issuing_bank_ref').id
            issuing_bank_ref_access_user = self.env['field.access'].search([('field_id', '=', issuing_bank_ref_field_id)]).user_ids.ids
            if self.env.user.id in issuing_bank_ref_access_user:
                rec.is_issuing_bank_ref_edit = True
            else:
                rec.is_issuing_bank_ref_edit = False
            lc_type_id_field_id = self.env.ref('custom_pledges.field_pledge_pledge__lc_type_id').id
            lc_type_id_access_user = self.env['field.access'].search([('field_id', '=', lc_type_id_field_id)]).user_ids.ids
            if self.env.user.id in lc_type_id_access_user:
                rec.is_lc_type_id_edit = True
            else:
                rec.is_lc_type_id_edit = False
            attachment_ids_field_id = self.env.ref('pledge_assets.field_pledge_pledge__attachment_ids').id
            attachment_ids_access_user = self.env['field.access'].search([('field_id', '=', attachment_ids_field_id)]).user_ids.ids
            if self.env.user.id in attachment_ids_access_user:
                rec.is_attachment_ids_edit = True
            else:
                rec.is_attachment_ids_edit = False
            x_studio_opining_date_field_id = self.env.ref('studio_customization.new_date_pledge_pled_d09d0fec-2c87-4558-be6d-e1b3392b5b8c').id
            x_studio_opining_date_access_user = self.env['field.access'].search([('field_id', '=', x_studio_opining_date_field_id)]).user_ids.ids
            if self.env.user.id in x_studio_opining_date_access_user:
                rec.is_x_studio_opining_date_edit = True
            else:
                rec.is_x_studio_opining_date_edit = False
            acceptance_date_field_id = self.env.ref('pledge_assets.field_pledge_pledge__acceptance_date').id
            acceptance_date_access_user = self.env['field.access'].search([('field_id', '=',acceptance_date_field_id)]).user_ids.ids
            if self.env.user.id in acceptance_date_access_user:
                rec.is_acceptance_date_edit = True
            else:
                rec.is_acceptance_date_edit = False
            x_studio_expire_date_field_id = self.env.ref('studio_customization.new_date_pledge_pled_5d846900-04ac-4b92-abab-43449845a9fb').id
            x_studio_expire_date_access_user = self.env['field.access'].search([('field_id', '=', x_studio_expire_date_field_id)]).user_ids.ids
            if self.env.user.id in x_studio_expire_date_access_user:
                rec.is_x_studio_expire_date_edit = True
            else:
                rec.is_x_studio_expire_date_edit = False
            date_of_extension_field_id = self.env.ref('custom_pledges.field_pledge_pledge__date_of_extension').id
            date_of_extension_access_user = self.env['field.access'].search([('field_id', '=', date_of_extension_field_id)]).user_ids.ids
            if self.env.user.id in date_of_extension_access_user:
                rec.is_date_of_extension_edit = True
            else:
                rec.is_date_of_extension_edit = False
            notes_field_id = self.env.ref('pledge_assets.field_pledge_pledge__notes').id
            notes_access_user = self.env['field.access'].search([('field_id', '=', notes_field_id)]).user_ids.ids
            if self.env.user.id in notes_access_user:
                rec.is_notes_edit = True
            else:
                rec.is_notes_edit = False
            validity_lines_field_id = self.env.ref('pledge_assets.field_pledge_pledge__validity_lines').id
            validity_lines_access_user = self.env['field.access'].search([('field_id', '=', validity_lines_field_id)]).user_ids.ids
            if self.env.user.id in validity_lines_access_user:
                rec.is_validity_lines_edit = True
            else:
                rec.is_validity_lines_edit = False
            expense_lines_field_id = self.env.ref('pledge_assets.field_pledge_pledge__expense_lines').id
            expense_lines_access_user = self.env['field.access'].search([('field_id', '=', expense_lines_field_id)]).user_ids.ids
            if self.env.user.id in expense_lines_access_user:
                rec.is_expense_lines_edit = True
            else:
                rec.is_expense_lines_edit = False
            deadline_ids_field_id = self.env.ref('custom_pledges.field_pledge_pledge__deadline_ids').id
            deadline_ids_access_user = self.env['field.access'].search([('field_id', '=', deadline_ids_field_id)]).user_ids.ids
            if self.env.user.id in deadline_ids_access_user:
                rec.is_deadline_ids_edit = True
            else:
                rec.is_deadline_ids_edit = False
            amendment_ids_field_id = self.env.ref('custom_pledges.field_pledge_pledge__amendment_ids').id
            amendment_ids_access_user = self.env['field.access'].search([('field_id', '=', amendment_ids_field_id)]).user_ids.ids
            if self.env.user.id in amendment_ids_access_user:
                rec.is_amendment_ids_edit = True
            else:
                rec.is_amendment_ids_edit = False
            payment_installation_ids_field_id = self.env.ref('custom_pledges.field_pledge_pledge__payment_installation_ids').id
            payment_installation_ids_access_user = self.env['field.access'].search([('field_id', '=', payment_installation_ids_field_id)]).user_ids.ids
            if self.env.user.id in payment_installation_ids_access_user:
                rec.is_payment_installation_ids_edit = True
            else:
                rec.is_payment_installation_ids_edit = False
            clearance_amount_field_id = self.env.ref('pledge_assets.field_pledge_pledge__clearance_amount').id
            clearance_amount_access_user = self.env['field.access'].search([('field_id', '=',clearance_amount_field_id)]).user_ids.ids
            if self.env.user.id in clearance_amount_access_user:
                rec.is_clearance_amount_edit = True
            else:
                rec.is_clearance_amount_edit = False
            clearance_attachments_field_id = self.env.ref('pledge_assets.field_pledge_pledge__clearance_attachement').id
            clearance_attachments_access_user = self.env['field.access'].search([('field_id', '=',clearance_attachments_field_id)]).user_ids.ids
            if self.env.user.id in clearance_attachments_access_user:
                rec.is_clearance_attachments_edit = True
            else:
                rec.is_clearance_attachments_edit = False

    @api.model
    def _read_group_stage_ids(self, stages, domain):
        return  self.env['pledge.stage'].search([])

    @api.depends('payment_installation_ids')
    def compute_paid_amount(self):
        """ Method to compute paid amount."""
        for rec in self:
            if rec.payment_installation_ids:
                amount = 0
                for installation in rec.payment_installation_ids:
                    amount = amount + installation.payment_amount
                rec.paid_amount = amount
            else:
                rec.paid_amount = 0

    @api.depends('amendment_ids')
    def compute_count_pending_amendments(self):
        """ Method to compute pending amendments."""
        for rec in self:
            if rec.amendment_ids:
                count = 0
                for amendment in rec.amendment_ids:
                    if amendment.status == 'pending':
                        count = count + 1
                rec.count_pending_amendments = count
            else:
                rec.count_pending_amendments = 0

    def search_amendments(self, operator, value):
        """ Method for filter amendments. """
        if operator == '>':
            res = self.env['pledge.pledge'].search([])
            res = res.filtered(lambda rec: rec.count_pending_amendments > value)
            return [('id', 'in', res.ids)]

        elif operator == '<':
            res = self.env['pledge.pledge'].search([])
            res = res.filtered(lambda rec: rec.count_pending_amendments < value)
            return [('id', 'in', res.ids)]
        elif operator == '>=':
            res = self.env['pledge.pledge'].search([])
            res = res.filtered(
                lambda rec: rec.count_pending_amendments >= value)
            return [('id', 'in', res.ids)]
        elif operator == '<=':
            res = self.env['pledge.pledge'].search([])
            res = res.filtered(
                lambda rec: rec.count_pending_amendments <= value)
            return [('id', 'in', res.ids)]
        elif operator == '=':
            res = self.env['pledge.pledge'].search([])
            res = res.filtered(
                lambda rec: value == rec.count_pending_amendments)
            return [('id', 'in', res.ids)]
        elif operator == '!=':
            res = self.env['pledge.pledge'].search([])
            res = res.filtered(
                lambda rec: rec.count_pending_amendments != value)
            return [('id', 'in', res.ids)]
        else:
            pass

    def write(self, vals):
        new_stage_id = self.env['pledge.stage'].browse(vals.get('stage_id'))
        if self.stage_id:
            if new_stage_id:
                if self.env.user.id not in self.stage_id.move_from_user_ids.ids:
                    raise UserError(_("You don't have access to move pledge from this stage."))
                if self.env.user.id not in new_stage_id.move_to_user_ids.ids:
                    raise UserError(
                        _("You don't have access to move pledge to this stage."))
                users = []
                if self.stage_id.is_from_user_notified:
                    users += self.stage_id.move_from_user_ids
                if new_stage_id.is_to_user_notified:
                    users += new_stage_id.move_to_user_ids
                if self.stage_id.other_users_notified:
                    users += self.stage_id.other_users_notified
                if new_stage_id.other_users_notified:
                    users += new_stage_id.other_users_notified
                for user in list(set(users)):
                    self.env['mail.activity'].sudo().create({
                        'display_name': 'Pledge Stage Changed',
                        'summary': 'ledge Stage Changed',
                        'note': "The pledge is moved from the stage " + self.stage_id.name + "to the stage " + new_stage_id.name + ".",
                        'date_deadline': fields.datetime.now(),
                        'user_id': int(user),
                        'res_id': self.id,
                        'res_model_id': self.env['ir.model'].sudo().search(
                            [('model', '=', 'pledge.pledge')], limit=1).id,
                        'activity_type_id': self.env.ref('custom_pledges.mail_activity_change_pledge_stage').id,
                    })
        return super(CustomPledges, self).write(vals)

class AlertDeadLine(models.Model):
    """ Alert deadline """
    _name = 'alert.deadline'

    pledge_id = fields.Many2one('pledge.pledge')
    deadline_entity = fields.Many2one('product.product',
                                      string="Deadline Entity")
    deadline = fields.Date(string="Deadline")
    alarm_entity = fields.Integer(string="Alarm Before ( days )")

    def send_deadline_notification(self):
        """ Method to send deadline notification."""
        for rec in self.env['alert.deadline'].search([]):
            date = rec.deadline - timedelta(days=rec.alarm_entity)
            if date == datetime.today().date():
                channel_id = self.env.ref(
                    'custom_pledges.deadline_notifications_channel')
                super_user = self.env['res.users'].browse(1)
                users = []
                for recepient in channel_id.channel_member_ids:
                    users.append(recepient.partner_id.id)
                message = _(
                    "Dear All,\n This email to remind you that this deadline will be met on for your information and "
                    "actions %s will have %s expires within %d Days"
                ) % (rec._get_html_link(),
                     rec.deadline_entity.name, rec.alarm_entity)
                channel_id.message_post(
                    author_id=super_user.partner_id.id,
                    body=_(message),
                    message_type='comment',
                    subtype_xmlid='mail.mt_comment',
                    partner_ids=users,
                )

                mail_values = {
                    'email_from': super_user.partner_id.email,
                    'subject': 'Deadline Reminder',
                    'email_to': ','.join([p.partner_id.email for p in
                                          channel_id.channel_member_ids]),
                }
                # Send email with template
                template = self.env.ref(
                    'custom_pledges.mail_template_deadline_pledge')
                template.with_context(email_from=mail_values['email_from'],
                    email_to=mail_values['email_to'],url= rec._get_html_link(),
                    pledge_name = rec.pledge_id.name,
                    deadline_entity= rec.deadline_entity.name,
                    notify_before= rec.alarm_entity).send_mail(
                    rec.pledge_id.id,
                    force_send=True
                )



class PaymentInstallation(models.Model):
    """ Payment Installation """
    _name = "payment.installation"

    payment_type = fields.Char(string="Payment Type")
    payment_amount = fields.Float(string="Payment Amount")
    currency_id = fields.Many2one('res.currency', string='Currency')
    payment_date = fields.Date(string="Payment Date")
    pledge_id = fields.Many2one('pledge.pledge', string="Pledge")
