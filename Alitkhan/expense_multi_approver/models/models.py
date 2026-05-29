# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError

class HrExpenseSheet(models.Model):
	_inherit = "hr.expense.sheet"

	user_ids = fields.Many2many("res.users", string="Approvers")
	next_approval_user = fields.Many2one("res.users", string="Next Approving User", compute="_get_next_approval")
	approval_lines = fields.One2many("hr.expense.sheet.approval", "sheet_id", copy=False)

	@api.depends("approval_lines", "user_ids")
	def _get_next_approval(self):
		for rec in self:
			remaining_aprovals = rec.approval_lines.filtered(lambda x: not x.approved)
			if remaining_aprovals:
				rec.next_approval_user = remaining_aprovals[0].user_id.id
			else:
				rec.next_approval_user = False

	@api.constrains('user_ids')
	def handle_user_ids_write(self):
		for rec in self:
			line_values = [(0, 0, {'user_id': user.id}) for user in rec.user_ids ]
			rec.write({
				'approval_lines': [(5, 0, 0)] + line_values
			})

	def action_submit_sheet(self):
		if len(self.approval_lines) == 0:
			raise UserError(_("Please enter at least one manager"))
		override = True if self.user_ids else False
		expense_values = {
			'state': 'submit',
			}
		self.write(expense_values)
		self.activity_update(override=override)

	def activity_update(self, override=False):
		if override:
			for expense_report in self.filtered(lambda hol: hol.state == 'submit'):
				expense_report.activity_schedule(
					'hr_expense.mail_act_expense_approval',
					user_id= expense_report.next_approval_user.id)


			self.filtered(lambda hol: hol.state == 'approve').activity_feedback(['hr_expense.mail_act_expense_approval'])
			self.filtered(lambda hol: hol.state == 'cancel').activity_unlink(['hr_expense.mail_act_expense_approval'])
		else:
			super(HrExpenseSheet, self).activity_update()

	def action_approve_expense_sheets(self):

		if not self.env.user.has_groups('hr_expense.group_hr_expense_team_approver'):
			raise UserError(_("Only Managers and HR Officers can approve expenses"))

		elif self.env.user.has_groups('hr_expense.group_hr_expense_user'):
			approval_line = self.approval_lines.filtered(lambda x: x.user_id.id == self.next_approval_user.id)
	
		else:
			is_authenticated_user = self.next_approval_user.id == self.env.user.id
			if not is_authenticated_user:
				raise UserError(_("You do not premission to approve this expense right now"))
			else:
				approval_line = self.approval_lines.filtered(lambda x: x.user_id.id == self.env.user.id)

		approval_line.approved = True
		approval_line.approved_date = fields.Datetime.now()
		approval_line.approved_by = self.env.user.id
		self.activity_unlink(['hr_expense.mail_act_expense_approval'], user_id=self.next_approval_user.id)

		approvals_done = all( self.approval_lines.mapped('approved') )

		if approvals_done:
			self.write({'state': 'approve', 'user_id': self.env.user.id})
		else:
			self.activity_schedule('hr_expense.mail_act_expense_approval', user_id= self.next_approval_user.id)

	def refuse_sheet(self, reason):
		# this function is copied from the original refuse_sheet() and edited
		# @M-Saeb
		# user = self.env.user
		if not self.env.user.has_groups('hr_expense.group_hr_expense_team_approver'):
			raise UserError(_("Only Managers and HR Officers can approve expenses"))
		elif not self.env.user.has_groups('hr_expense.group_hr_expense_manager'):
			if self.employee_id.user_id == self.env.user:
				raise UserError(_("You cannot refuse your own expenses"))

		self.write({'state': 'cancel'})
		for sheet in self:
			sheet.message_post_with_view('hr_expense.hr_expense_template_refuse_reason', values={'reason': reason, 'is_sheet': True, 'name': self.name})
		self.activity_update()

		for line in self.approval_lines:
			line.approved = False
			line.approved_date = False
		self.activity_unlink(['hr_expense.mail_act_expense_approval'], user_id = self.next_approval_user.id)

class HrExpenseSheetAprovals(models.Model):
	_name = "hr.expense.sheet.approval"
	_order = "sequence"

	sequence = fields.Integer("Sequence")
	user_id = fields.Many2one("res.users", "Employee", required=True, readonly=True)
	approved_by = fields.Many2one("res.users", readonly=True)
	sheet_id = fields.Many2one("hr.expense.sheet", readonly=True, ondelete="cascade")
	approved = fields.Boolean(readonly=True)
	approved_date = fields.Datetime("Approved Date", readonly=True)
