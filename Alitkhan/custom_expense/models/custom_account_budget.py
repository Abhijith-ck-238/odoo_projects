from datetime import timedelta, datetime
from odoo import models, fields, api, _
from odoo.exceptions import UserError


class CustomCrossoveredBudget(models.Model):
    _inherit = "budget.analytic"

    # TODO: The below content is commented because it is not required in the latest database.The related functionality is no longer part of the current business process.Kept only for reference during migration and validation.


    # @api.model
    # def get_accounting_users(self):
    #     accounting_user = self.env['ir.config_parameter'].sudo().get_param(
    #         'custom_expense.accounting_users_to_notify')
    #     new_accounting_user = accounting_user.translate(
    #         {ord(c): None for c in "[]"})
    #     li = list(new_accounting_user.split(","))
    #     return self.env['res.users'].search(
    #         [('id', 'in', li)]).ids

    # @api.model
    # def get_accounting_users(self):
    #     accounting_user = self.env['ir.config_parameter'].sudo().get_param(
    #         'custom_expense.accounting_users_to_notify', default="[]"
    #     )
    #
    #     # Ensure accounting_user is a string before processing
    #     if not accounting_user or not isinstance(accounting_user, str):
    #         return []
    #
    #     # Clean the string and convert it to a list of integers
    #     new_accounting_user = accounting_user.replace("[", "").replace("]", "")
    #     user_ids = [int(user_id.strip()) for user_id in
    #                 new_accounting_user.split(",") if user_id.strip().isdigit()]
    #
    #     return self.env['res.users'].search([('id', 'in', user_ids)]).ids
    #
    expense_state = fields.Selection([
        ('draft_budget', 'Draft'),
        ('budget_check', 'Budget Check'),
        ('dm_approval', 'DM Approval'),
        ('gm_approval', 'GM Approval'),
        ('ac_approval', 'AC Approval'),
        ('confirmed', 'Confirmed'),
        ('cancel', 'Cancelled'),
        ('extend_budget', 'Extend Budget')

    ], 'Status', default='draft_budget', index=True, required=True,
        readonly=True, copy=False, tracking=True)
    is_dm = fields.Boolean(
        compute="compute_is_dm")
    is_gm = fields.Boolean(
        compute="compute_is_gm")
    is_ac = fields.Boolean(
        compute="compute_is_ac")
    is_user = fields.Boolean(
        compute="compute_is_user")
    is_extend_budget_state = fields.Boolean(string="Is extend budget state",
                                            default=False)

    accounting_user_ids = fields.Many2many('res.users',
                                           stored=True)
    remaining_budget = fields.Float(string="Remaining Budget")
    #
    # @api.model
    # def send_budget_deadline_notification(self):
    #     """ Method to send deadline notification."""
    #     res = self.env['budget.analytic'].search([])
    #     for rec in res:
    #         users = self.env['ir.config_parameter'].sudo().get_param(
    #             'custom_expense.budget_reminder_user_ids')
    #         if users == []:
    #             new_users = users.translate(
    #                 {ord(c): None for c in "[]"})
    #             li = list(new_users.split(","))
    #         else:
    #             li = []
    #         date = rec.date_to - timedelta(days=7)
    #         li.append(rec.user_id.id)
    #         users_record = self.env['res.users'].browse(
    #             int(user) for user in li)
    #         if date == datetime.today().date():
    #             partner_ids = [p.partner_id.id for p in users_record]
    #             super_user = self.env['res.users'].browse(1)
    #
    #             # Real clickable link for both chatter and email
    #             message = _(
    #                 "Dear All,\n This email to remind you that this deadline will be met on for your information and "
    #                 "actions %s will end within 7 days"
    #             ) % (rec._get_html_link())
    #             channel_id = self.env['discuss.channel'].search(
    #                 [('name', 'ilike', 'Accounting department ')])
    #             channel_id.message_post(
    #                 author_id=super_user.partner_id.id,
    #                 body=_(message),
    #                 message_type='comment',
    #                 subtype_xmlid='mail.mt_comment',
    #                 partner_ids=partner_ids,
    #             )
    #             message_body = _(
    #                 "Dear %s,\n This email to remind you that this deadline will be met on for your information and "
    #                 "actions %s will end within 7 days"
    #             ) % (rec.user_id.name, rec._get_html_link())
    #             rec.message_post(
    #                 body=message_body,
    #                 message_type='comment',
    #                 subtype_xmlid='mail.mt_comment',
    #                 partner_ids=[rec.user_id.partner_id.id],
    #             )
    #
    # def compute_remaining_budget(self):
    #     for rec in self:
    #         total_budget = sum(rec.budget_line_ids.mapped('budget_amount'))
    #
    #         budget_line = self.env['budget.line'].search([
    #             ('auto_account_id', '!=', False),
    #             ('budget_analytic_id', '=', rec.id)
    #         ], limit=1)
    #
    #         if budget_line and budget_line.auto_account_id.line_ids:
    #             rec.remaining_budget = budget_line.auto_account_id.sudo().remaining_budget_amount
    #         else:
    #             rec.remaining_budget = total_budget
    #
    # @api.depends("user_id")
    # def compute_is_user(self):
    #     """ Checks if user is responsible for the current record
    #     """
    #     for rec in self:
    #         if rec.user_id.id == self._uid:
    #             rec.is_user = True
    #         else:
    #             rec.is_user = False
    #
    # @api.depends("user_id")
    # def compute_is_dm(self):
    #     """ Checks if user is dm
    #     """
    #     for rec in self:
    #         # emp_obj = rec.user_id.emp_id
    #         # res = self.env['hr.employee.public'].browse(emp_obj.id)
    #         # res = self.env['hr.employee'].browse(emp_obj.id)
    #         if rec.user_id.emp_id.budget_manager.user_id.id == self._uid:
    #             rec.is_dm = True
    #         else:
    #             rec.is_dm = False
    #
    # @api.depends("user_id")
    # def compute_is_gm(self):
    #     """ Checks if user is gm
    #     """
    #     for rec in self:
    #         # emp_obj = rec.user_id.emp_id
    #         # res = self.env['hr.employee.public'].browse(emp_obj.id)
    #         if rec.user_id.emp_id.director_id.id == self._uid:
    #             rec.is_gm = True
    #         else:
    #             rec.is_gm = False
    #
    # # @api.depends("user_id")
    # # def compute_is_ac(self):
    # #     """ Checks if user is Ac
    # #     """
    # #     accounting_user = self.env['ir.config_parameter'].sudo().get_param(
    # #         'custom_expense.accounting_users_to_notify')
    # #     new_accounting_user = accounting_user.translate(
    # #         {ord(c): None for c in "[]"})
    # #     li = list(new_accounting_user.split(","))
    # #     for user_id in li:
    # #         if int(user_id) == self.env.user.id:
    # #             self.is_ac = True
    # #             break
    # #         else:
    # #             self.is_ac = False
    #
    # @api.depends("user_id")
    # def compute_is_ac(self):
    #     """ Checks if user is AC """
    #     self.is_ac = False  # Default value
    #
    #     accounting_user = self.env['ir.config_parameter'].sudo().get_param(
    #         'custom_expense.accounting_users_to_notify', default="[]"
    #     )
    #
    #     if not accounting_user or not isinstance(accounting_user, str):
    #         return  # Exit if no valid data
    #
    #     # Remove brackets and split
    #     new_accounting_user = accounting_user.replace("[", "").replace("]", "")
    #     user_list = [user_id.strip() for user_id in
    #                  new_accounting_user.split(",") if
    #                  user_id.strip().isdigit()]
    #
    #     # Convert to integer set for easy checking
    #     user_ids = {int(user_id) for user_id in user_list}
    #
    #     if self.env.user.id in user_ids:
    #         self.is_ac = True
    #
    # def _send_budget_notification(self, subject, message, user_name=False):
    #     action_id = self.env.ref(
    #         "custom_expense.hr_expense_actions_my_budget").id
    #     base_url = self.env["ir.config_parameter"].sudo().get_param(
    #         "web.base.url")
    #
    #     # Option 1: Send email directly without template
    #     body_html = f"""
    #         <div>
    #             <p>Dear {user_name if user_name else self.user_id.name},</p>
    #             <p>{message}</p>
    #             <p>
    #                 <a href="{base_url}/web#id={self.id}&action={action_id}&model=budget.analytic&view_type=form"
    #                    style="background-color:#875A7B; padding: 8px 16px; text-decoration: none; color: #fff; border-radius: 5px;">
    #                     View Details
    #                 </a>
    #             </p>
    #             <p>Best regards,</p>
    #             <p>{self.company_id.name}</p>
    #         </div>
    #     """
    #
    #     # Send email directly using mail.mail
    #     mail_values = {
    #         'email_to': self.user_id.login,
    #         'email_from': self.env.user.email_formatted,
    #         'subject': subject,
    #         'body_html': body_html,
    #         'model': 'budget.analytic',
    #         'res_id': self.id,
    #     }
    #
    #     mail = self.env['mail.mail'].create(mail_values)
    #     mail.send()
    #
    # def action_budget_cancel(self):
    #     self.write({"state": "canceled", "expense_state": "cancel"})
    #
    #     self._send_budget_notification(
    #         subject="Budget : Budget Cancelled",
    #         message=f"Your Budget {self.name} is cancelled."
    #     )
    #
    # def action_budget_confirm(self):
    #     self.write({"state": "confirmed", "expense_state": "confirmed"})
    #
    #     self._send_budget_notification(
    #         subject="Budget : Budget Confirmed",
    #         message=f"Your Budget {self.name} is confirmed."
    #     )
    #
    # def action_budget_draft(self):
    #     self.write({'state': 'draft'})
    #     self.write({'expense_state': 'draft_budget'})
    #
    # def action_budget_validate(self):
    #     for budget_line in self.budget_line_ids:
    #         if budget_line.amount_to_extend == 0.0:
    #             pass
    #         else:
    #             budget_line.budget_amount = budget_line.budget_amount + budget_line.amount_to_extend
    #             budget_line.amount_to_extend = 0.0
    #     self.write({'state': 'validate'})
    #     self.is_extend_budget_state = True
    #     self.write({'expense_state': 'confirmed'})
    #
    # def total_amount_to_extend(self):
    #     total = 0.0
    #     for budget_line in self.budget_line_ids:
    #         total = total + budget_line.amount_to_extend
    #     return total
    #
    # def action_check_budget(self):
    #     has_planned_amount = any(
    #         line.budget_amount == 0.0 for line in self.budget_line_ids)
    #     if has_planned_amount:
    #         raise UserError(_("The planned amount cannot be 0.0"))
    #
    #     approver_user = self.env["ir.config_parameter"].sudo().get_param(
    #         "custom_expense.budget_check_approver")
    #     if approver_user:
    #         approver_ids = list(map(int, approver_user.translate(
    #             {ord(c): None for c in "[]"}).split(",")))
    #
    #         for user_id in approver_ids:
    #             res_user = self.env["res.users"].browse(user_id)
    #
    #             message = f"You have a Budget {self.name} for {self.user_id.name} to Approve."
    #             self._send_budget_notification(
    #                 subject="Budget: Approval Notification",
    #                 message=message,
    #                 user_name=res_user.emp_id.name
    #             )
    #
    #         self.write({"expense_state": "budget_check"})
    #     else:
    #         self.action_budget_confirm_team_approver()
    #
    # def action_budget_confirm_team_approver(self):
    #     has_planned_amount = any(
    #         line.budget_amount == 0.0 for line in self.budget_line_ids)
    #     if has_planned_amount:
    #         raise UserError(_("The planned amount cannot be 0.0"))
    #
    #     total = self.total_amount_to_extend()
    #     approval_name = self.user_id.emp_id.budget_manager.name
    #     approval_email_to = self.user_id.emp_id.budget_manager.work_email
    #
    #     if total == 0.0:
    #         approval_message = f"You have a Budget {self.name} for {self.user_id.name} to Approve."
    #     else:
    #         approval_message = f"You have a request for an extended budget for Budget {self.name} to Approve."
    #
    #     self._send_budget_notification(
    #         subject="Budget : Approval Notification",
    #         message=approval_message,
    #         user_name=approval_name
    #     )
    #
    #     self.write({'expense_state': 'dm_approval'})
    #
    # def action_approve_dm(self):
    #     emp_obj = self.user_id.emp_id
    #     res = self.env["hr.employee.public"].browse(emp_obj.id)
    #
    #     # If the current user is the director of the employee
    #     if res.director_id.id == self._uid:
    #         total = self.total_amount_to_extend()
    #         accounting_users = self.env["ir.config_parameter"].sudo().get_param(
    #             "custom_expense.accounting_users_to_notify")
    #
    #         if accounting_users:
    #             accounting_user_ids = list(map(int, accounting_users.translate(
    #                 {ord(c): None for c in "[]"}).split(",")))
    #
    #             for user_id in accounting_user_ids:
    #                 res_user = self.env["res.users"].browse(user_id)
    #
    #                 if total == 0.0:
    #                     approval_message = f"You have a Budget {self.name} for {self.user_id.name} to Approve."
    #                 else:
    #                     approval_message = f"You have a request for an extended budget for Budget {self.name} to check."
    #
    #                 self._send_budget_notification(
    #                     subject="Budget: Accounting Approval",
    #                     message=approval_message,
    #                     user_name=res_user.name
    #                 )
    #
    #             self.write({"expense_state": "ac_approval"})
    #
    # def action_reject_dm(self):
    #     total = self.total_amount_to_extend()
    #
    #     subject = "Budget: Request for Extend Budget Refused" if total != 0.0 else "Budget: Budget Refused"
    #     message = (
    #         f"Your Request for extend budget for the Budget {self.name} is Refused by DM."
    #         if total != 0.0 else
    #         f"Your Budget {self.name} is Refused by DM."
    #     )
    #
    #     self._send_budget_notification(subject=subject, message=message)
    #
    #     self.write({"expense_state": "cancel", "state": "canceled"})
    #
    # def action_approve_gm(self):
    #     total = self.total_amount_to_extend()
    #     accounting_users = self.env["ir.config_parameter"].sudo().get_param(
    #         "custom_expense.accounting_users_to_notify")
    #
    #     if accounting_users:
    #         user_ids = list(map(int, accounting_users.translate(
    #             {ord(c): None for c in "[]"}).split(",")))
    #
    #         for user_id in user_ids:
    #             res_user = self.env["res.users"].browse(user_id)
    #
    #             message = (
    #                 f"You have a Budget {self.name} for {self.user_id.name} to Approve."
    #                 if total == 0.0 else
    #                 f"You have a request for an extended budget for Budget {self.name} to check."
    #             )
    #
    #             self._send_budget_notification(
    #                 subject="Budget: Accounting Approval",
    #                 message=message,
    #                 user_name=res_user.name
    #             )
    #
    #     self.write({"expense_state": "ac_approval"})
    #
    # def action_reject_gm(self):
    #     total = self.total_amount_to_extend()
    #
    #     # Reset budget extension if total is not 0.0
    #     if total != 0.0:
    #         for line in self.budget_line_ids:
    #             if line.amount_to_extend:
    #                 line.amount_to_extend = 0
    #
    #     subject = "Budget: Request for Extend Budget Refused" if total != 0.0 else "Budget: Budget Refused"
    #     message = (
    #         f"Your Request for extend budget for the Budget {self.name} is Refused by GM."
    #         if total != 0.0 else
    #         f"Your Budget {self.name} is Refused by GM."
    #     )
    #
    #     # Use `_send_budget_notification` to send the email
    #     self._send_budget_notification(subject=subject, message=message)
    #
    #     self.write({"expense_state": "cancel", "state": "canceled"})
    #
    # def action_approve_ac(self):
    #     total = self.total_amount_to_extend()
    #
    #     if total != 0.0:
    #         # Update budget amounts
    #         for line in self.budget_line_ids:
    #             if line.amount_to_extend:
    #                 line.budget_amount += line.amount_to_extend
    #                 line.amount_to_extend = 0
    #         message = f"Your Request to Extend Budget {self.name} is confirmed by AC."
    #     else:
    #         message = f"Your Budget {self.name} is confirmed by AC."
    #
    #     self._send_budget_notification(subject="Budget: Budget Confirmed",
    #                                    message=message)
    #
    #     self.write({"expense_state": "confirmed", "state": "confirmed"})
    #
    # def action_reject_ac(self):
    #     total = self.total_amount_to_extend()
    #
    #     if total != 0.0:
    #         # Reset extended amounts
    #         for line in self.budget_line_ids:
    #             if line.amount_to_extend:
    #                 line.amount_to_extend = 0
    #         subject = "Budget: Request for Extend Budget Refused"
    #         message = f"Your request to extend the budget for {self.name} has been refused by AC."
    #     else:
    #         subject = "Budget: Budget Refused"
    #         message = f"Your Budget {self.name} has been refused by AC."
    #
    #     self._send_budget_notification(subject=subject, message=message)
    #
    #     self.write({"expense_state": "cancel", "state": "canceled"})
    #
    # def action_extend_budget(self):
    #     self.write({'expense_state': 'extend_budget'})
    #     budget_form_view = self.env.ref(
    #         'custom_expense.crossovered_budget_view_extend')
    #
    #     return {
    #         'type': 'ir.actions.act_window',
    #         'name': 'Budget',
    #         'res_model': 'budget.analytic',
    #         'view_mode': 'form',
    #         'views': [(budget_form_view.id, 'form')],
    #         'res_id': self.id,
    #         'target': 'current',
    #     }
    #
    # def action_request_extend_budget(self):
    #     has_atleat_one_amount = False
    #     for budget_line in self.budget_line_ids:
    #         if budget_line.amount_to_extend != 0.0:
    #             has_atleat_one_amount = True
    #             break
    #         else:
    #             pass
    #     if has_atleat_one_amount == True:
    #         self.action_budget_confirm_team_approver()
    #     else:
    #         raise UserError(
    #             _("You should have atleast one budget line have Amount to Extend "))
    #
    # def action_reset_to_draft(self):
    #     self.write({'expense_state': 'extend_budget'})
    #     self.write({'state': 'draft'})
    #
    # def action_accounting_user_extend_budget(self):
    #     self.is_extend_budget_state = False
    #     self.write({'expense_state': 'extend_budget'})
    #
    # def action_accounting_user_extend(self):
    #     for budget_line in self.budget_line_ids:
    #         if budget_line.amount_to_extend:
    #             budget_line.planned_amount = budget_line.budget_amount + budget_line.amount_to_extend
    #             budget_line.amount_to_extend = 0
    #     self.write({'expense_state': 'confirmed'})
    #     self.is_extend_budget_state = True
