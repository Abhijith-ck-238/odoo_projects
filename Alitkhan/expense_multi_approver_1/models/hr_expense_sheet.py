# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError


class HrExpenseSheet(models.Model):
    _inherit = "hr.expense.sheet"

    def _get_default_next_action(self):
        return {'type': 'ir.actions.client', 'tag': 'soft_reload'}

    def _build_sheet_level_warning_action(self, warning_messages, next_action=None):
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Expense Warning'),
                'message': '\n\n'.join(warning_messages),
                'type': 'warning',
                'sticky': True,
                'next': next_action or self._get_default_next_action(),
            }
        }

    def _get_sheet_level_warnings(self):
        warning_messages = []
        blocking_messages = []
        is_account_manager = self.env.user.has_group('account.group_account_manager')

        for sheet in self:
            sheet_messages = []
            same_receipt_lines = sheet.expense_line_ids.filtered('same_receipt_expense_ids')
            if same_receipt_lines:
                sheet_messages.append(_(
                    "Duplicate attachment found in another expense for: %s"
                ) % ', '.join(same_receipt_lines.mapped('name')))

            duplicated_attachment_lines = self.env['hr.expense']
            for line in sheet.expense_line_ids.filtered('attachment_ids'):
                checksums = [checksum for checksum in line.attachment_ids.mapped('checksum') if checksum]
                if len(checksums) != len(set(checksums)):
                    duplicated_attachment_lines |= line
            if duplicated_attachment_lines:
                sheet_messages.append(_(
                    "Duplicate attachment found within the same expense for: %s"
                ) % ', '.join(duplicated_attachment_lines.mapped('name')))

            budget_policy_field = sheet._fields.get('budget_policy_id')
            budget_owner = budget_policy_field and sheet.budget_policy_id.budget_owner_id or False
            if budget_owner and budget_owner != self.env.user:
                owner_message = _(
                    "Approver %s is not the budget owner %s."
                ) % (self.env.user.name, budget_owner.name)
                if is_account_manager:
                    sheet_messages.append(owner_message)
                else:
                    blocking_messages.append("%s\n- %s" % (sheet.display_name, owner_message))

            if sheet_messages:
                warning_messages.append("%s\n%s" % (
                    sheet.display_name,
                    '\n'.join("- %s" % message for message in sheet_messages),
                ))

        return warning_messages, blocking_messages

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
            line_values = [(0, 0, {'user_id': user.id}) for user in rec.user_ids]
            rec.write({
                'approval_lines': [(5, 0, 0)] + line_values
            })

    def action_submit_sheet(self):
        for rec in self:
            if rec.is_old_data:
                # raise error while using this method in old datas
                raise UserError(
                    _("sorry, You cannot update this data. This is old data."))
        if len(self.approval_lines) == 0:
            raise UserError(_("Please enter at least one manager"))
        override = True if self.user_ids else False
        self.approval_state = 'submit'
        self.activity_update(override=override)

    def activity_update(self, override=False):
        if override:
            for expense_report in self.filtered(lambda hol: hol.state == 'submit'):
                next_user = expense_report.next_approval_user
                if next_user:
                    expense_report.activity_schedule(
                        'hr_expense.mail_act_expense_approval',
                        user_id=expense_report.next_approval_user.id)
                    expense_report.message_post(
                        body=_(
                            "Expense submitted. Waiting for approval from: %s"
                        ) % next_user.name,
                        message_type="comment",
                        subtype_xmlid="mail.mt_note",
                    )
            self.filtered(lambda hol: hol.state == 'approve').activity_feedback(
                ['hr_expense.mail_act_expense_approval'])
            self.filtered(lambda hol: hol.state == 'cancel').activity_unlink(['hr_expense.mail_act_expense_approval'])
        else:
            super(HrExpenseSheet, self).activity_update()

    def action_approve_expense_sheets(self):
        warning_messages, blocking_messages = self._get_sheet_level_warnings()
        if blocking_messages:
            return self._build_sheet_level_warning_action(blocking_messages)

        # Prevent old data update
        for rec in self:
            if rec.is_old_data:
                raise UserError(_("Sorry, you cannot update this data. This is old data."))

        # Allow account managers to approve any expense
        is_account_manager = self.env.user.has_group('account.group_account_manager')
        is_hr_approver = self.env.user.has_group('hr_expense.group_hr_expense_team_approver')

        if not is_account_manager and not is_hr_approver:
            raise UserError(_("Only Managers and HR Officers can approve expenses"))

        sheets_to_finalize = self.env['hr.expense.sheet']

        for sheet in self:
            # Account managers can bypass approval flow checks
            if not is_account_manager:

                if sheet.next_approval_user != self.env.user:
                    raise UserError(_(
                        "You do not have permission to approve this expense right now. "
                        "The next approver is: %s"
                    ) % (sheet.next_approval_user.name or _("(not set)")))

                approval_line = sheet.approval_lines.filtered(
                    lambda l: l.user_id == self.env.user and not l.approved
                )

                if not approval_line:
                    raise UserError(_("You have already approved this expense."))

                approval_line.write({
                    'approved': True,
                    'approved_date': fields.Datetime.now(),
                    'approved_by': self.env.user.id,
                })

                # Remove current activity
                sheet.activity_unlink(
                    ['hr_expense.mail_act_expense_approval'],
                    user_id=self.env.user.id
                )

                # If all approved → finalize later
                if all(sheet.approval_lines.mapped('approved')):
                    sheets_to_finalize |= sheet
                else:
                    # Move to next approver
                    sheet.activity_schedule(
                        'hr_expense.mail_act_expense_approval',
                        user_id=sheet.next_approval_user.id
                    )

            else:
                # Account manager → directly finalize
                sheet.approval_lines.write({
                    'approved': True,
                    'approved_date': fields.Datetime.now(),
                    'approved_by': self.env.user.id,
                })

                sheet.activity_unlink(['hr_expense.mail_act_expense_approval'])
                sheets_to_finalize |= sheet

        # ✅ Call super ONCE for all sheets that need final approval
        if sheets_to_finalize:
            res = super(HrExpenseSheet, sheets_to_finalize).action_approve_expense_sheets()
            sheets_to_finalize.write({
                'state': 'approve',
                'user_id': self.env.user.id
            })
            return res




    @api.depends_context('uid')
    @api.depends('employee_id')
    def _compute_can_approve(self):
        """Overwrites this method to remove the restriction of employee for approving their own expense."""
        is_team_approver = self.env.user.has_group('hr_expense.group_hr_expense_team_approver') or self.env.su
        is_approver = self.env.user.has_group('__export__.res_groups_924_81677801') or self.env.su
        is_hr_admin = self.env.user.has_group('hr_expense.group_hr_expense_manager') or self.env.su

        for sheet in self:
            reason = False
            if not is_team_approver:
                reason = _("%s: Your are not a Manager or HR Officer", sheet.name)

            elif not is_hr_admin:
                if sheet.next_approval_user == self.env.user:
                    reason = False  # explicitly permitted
                else:
                    sheet_employee = sheet.employee_id
                    current_managers = sheet_employee.expense_manager_id \
                                       | sheet_employee.parent_id.user_id \
                                       | sheet_employee.department_id.manager_id.user_id \
                                       | sheet.user_id

                    if self.env.user not in current_managers and not is_approver and sheet_employee.expense_manager_id.id != self.env.user.id:
                        reason = _("%s: It is not from your department", sheet.name)

            sheet.can_approve = not reason
            sheet.cannot_approve_reason = reason

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
            sheet.message_post_with_view('hr_expense.hr_expense_template_refuse_reason',
                                         values={'reason': reason, 'is_sheet': True, 'name': self.name})
        self.activity_update()

        for line in self.approval_lines:
            line.approved = False
            line.approved_date = False
        self.activity_unlink(['hr_expense.mail_act_expense_approval'], user_id=self.next_approval_user.id)

