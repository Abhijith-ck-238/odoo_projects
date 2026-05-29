# -*- coding: utf-8 -*-
from odoo import models, fields, _, api
from odoo.exceptions import ValidationError, UserError


class HrExpenseSheet(models.Model):
    _inherit = 'hr.expense.sheet'

    def _get_default_next_action(self):
        return {'type': 'ir.actions.client', 'tag': 'soft_reload'}

    def _build_sheet_level_warning_action(self, warning_messages, next_action=None):
        """Build a warning notification action that auto-dismisses"""
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Duplicated Attachment'),
                'message': '\n\n'.join(warning_messages),
                'type': 'warning',
                'sticky': False,
                'next': next_action or self._get_default_next_action(),
            }
        }

    def _get_sheet_level_warnings(self):
        """Get warning messages for duplicate attachments in expense sheets."""
        warning_messages = []
        blocking_messages = []
        is_account_manager = self.env.user.has_group('account.group_account_manager')

        for sheet in self:
            sheet_messages = []

            # Check for duplicate attachments in other expenses
            same_receipt_lines = sheet.expense_line_ids.filtered('same_receipt_expense_ids')
            if same_receipt_lines:
                sheet_messages.append(_(
                    "Duplicate attachment found in another expense for: %s"
                ) % ', '.join(same_receipt_lines.mapped('name')))

            # Check for duplicate attachments within the same expense
            duplicated_attachment_lines = self.env['hr.expense']
            for line in sheet.expense_line_ids.filtered('attachment_ids'):
                checksums = [checksum for checksum in line.attachment_ids.mapped('checksum') if checksum]
                if len(checksums) != len(set(checksums)):
                    duplicated_attachment_lines |= line

            if duplicated_attachment_lines:
                sheet_messages.append(_(
                    "Duplicate attachment found within the same expense for: %s"
                ) % ', '.join(duplicated_attachment_lines.mapped('name')))

            budget_owner = sheet.budget_policy_id.budget_owner_id if 'budget_policy_id' in sheet._fields else False
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

    budget_policy_id = fields.Many2one(
        'hr.expense.budget.policy',
        string="Budget Policy",
        ondelete='set null',
        help="Budget policy applied on this expense sheet.",
        tracking=True,
    )

    available_amount = fields.Monetary(
        string="Available Amount",
        currency_field='currency_id',
        related='budget_policy_id.consumption_ids.available_amount',
        store=False,
        readonly=True
    )

    vendor_bill_ref = fields.Char(
        string='Vendor Bill',
        related="account_move_ids.name",
        store=False,
        readonly=True,
        help="Reference number of the vendor bill generated from this expense report"
    )

    # Override the journal to be derived from the budget policy or company default
    employee_journal_id = fields.Many2one(
        'account.journal',
        string="Journal",
        compute='_compute_employee_journal_id',
        store=True,
        check_company=True,
        domain=[('type', '=', 'purchase')],
    )

    @api.model
    def create(self, vals):
        """Apply analytic distribution when budget_policy_id is set via import"""
        sheet = super(HrExpenseSheet, self).create(vals)
        policy = vals.get('budget_policy_id')
        if policy and sheet.budget_policy_id.analytic_distribution:
            for line in sheet.expense_line_ids:
                line.analytic_distribution = sheet.budget_policy_id.analytic_distribution
        if policy:
            journal = self.env["hr.expense.budget.policy"].browse(policy).journal_id.id
            if journal:
                vals['employee_journal_id'] = journal
        return sheet

    def write(self, vals):
        """Update the journal and analytic distribution in the journal entry while updating here"""
        res = super(HrExpenseSheet, self).write(vals)
        # Apply analytic distribution when budget_policy_id is set via import
        if 'budget_policy_id' in vals:
            for sheet in self:
                if sheet.budget_policy_id and sheet.budget_policy_id.analytic_distribution:
                    for line in sheet.expense_line_ids:
                        line.analytic_distribution = sheet.budget_policy_id.analytic_distribution

        expense_commands = vals.get('expense_line_ids')
        updated_expense_map = {}

        if expense_commands:
            for command in expense_commands:
                # command format: (operation, id, values)
                if command[0] == 1:  # update existing record
                    expense_id = command[1]
                    values = command[2]

                    if 'analytic_distribution' in values:
                        updated_expense_map[expense_id] = values['analytic_distribution']

        if updated_expense_map:
            for sheet in self:
                draft_moves = sheet.account_move_ids.filtered(lambda m: m.state == 'draft')

                for move in draft_moves:
                    for line in move.invoice_line_ids:
                        if line.expense_id.id in updated_expense_map:
                            line.write({
                                'analytic_distribution': updated_expense_map[line.expense_id.id]
                            })
        if vals.get("employee_journal_id"):
            for sheet in self:
                draft_moves = sheet.account_move_ids.filtered(lambda m: m.state == 'draft')
                draft_moves.write({
                    "journal_id": vals.get('employee_journal_id'),
                })
        return res

    @api.onchange('budget_policy_id')
    def _onchange_budget_policy_id(self):
        """Update analytic distribution on expense lines based on the selected budget policy."""
        for sheet in self:
            policy = sheet.budget_policy_id

            # If policy removed → clear analytic distribution
            if not policy:
                for line in sheet.expense_line_ids:
                    line.analytic_distribution = False
                continue

            analytic_accounts = policy.analytic_distribution

            # If policy has no analytic distribution → clear
            if not analytic_accounts:
                for line in sheet.expense_line_ids:
                    line.analytic_distribution = False
                continue

            # Otherwise apply policy distribution
            for line in sheet.expense_line_ids:
                line.analytic_distribution = analytic_accounts

    def action_submit_sheet(self):
        """Prevent submission if total expenses exceed the available budget amount."""
        for sheet in self:
            # if not sheet.budget_policy_id:
            #     continue
            # if sheet.advance:
            #     # Advance payment sheet: the full advance amount must be within available budget
            #     total_to_compare = sheet.total_amount
            # elif sheet.advance_sheet_id:
            #     # Clearing expense: only the amount exceeding the advance counts against remaining budget
            total_to_compare = sheet.total_amount
            if sheet.advance_sheet_id:
                # If clearing an advance, only the amount exceeding the advance counts against remaining budget
                clearing_amount = min(sheet.total_amount, sheet.advance_sheet_residual)
                total_to_compare = sheet.total_amount - clearing_amount
            # else:
            #     total_to_compare = sheet.total_amount

            if total_to_compare > sheet.available_amount:
                # if sheet.advance:
                #     raise ValidationError(
                #         _("Cannot submit advance payment: the requested amount (%.2f) exceeds "
                #           "the available budget (%.2f). Please reduce the advance amount or "
                #           "request a budget increase before proceeding.")
                #         % (total_to_compare, sheet.available_amount)
                #     )
                raise ValidationError(
                    _("Total expense (%.2f) cannot be more than the available amount (%.2f).")
                    % (total_to_compare, sheet.available_amount)
                )
        return super(HrExpenseSheet, self).action_submit_sheet()

    def action_approve_expense_sheets(self):
        """
        Approve expense sheets with warnings for duplicate attachments only.
        Warnings are displayed but do NOT block approval.
        """
        # Get warnings for duplicate attachments
        warning_messages, blocking_messages = self._get_sheet_level_warnings()

        if blocking_messages:
            return self._build_sheet_level_warning_action(blocking_messages)

        # # Budget restriction: block approval of advance payment sheets that exceed the budget
        # for sheet in self:
        #     if not sheet.budget_policy_id:
        #         continue
        #     if sheet.advance:
        #         # Advance payment sheet: the full advance amount must be within available budget
        #         total_to_compare = sheet.total_amount
        #         if total_to_compare > sheet.available_amount:
        #             raise UserError(
        #                 _("Cannot approve advance payment '%s': the requested amount (%.2f) "
        #                   "exceeds the available budget (%.2f). Budget is not sufficient.")
        #                 % (sheet.name, total_to_compare, sheet.available_amount)
        #             )
        #
        # # Execute the parent approve action
        result = super(HrExpenseSheet, self).action_approve_expense_sheets()

        # if result and result.get('tag') == 'display_notification':
        #     result = self._get_default_next_action()

        if warning_messages:
            return self._build_sheet_level_warning_action(
                warning_messages,
                result or self._get_default_next_action(),
            )

        return result

    @api.onchange('expense_line_ids')
    def _onchange_expense_line_ids(self):
        """Apply analytic distribution to newly added expense lines"""
        if self.budget_policy_id and self.budget_policy_id.analytic_distribution:
            for line in self.expense_line_ids:
                if not line.analytic_distribution:
                    line.analytic_distribution = self.budget_policy_id.analytic_distribution

    def _compute_is_editable(self):
        """Allow edit access for approvers when the sheet is in submit state"""
        all_approver = self.env.user.has_group('__export__.res_groups_924_81677801')

        for sheet in self:
            if all_approver and sheet.state == 'submit':
                sheet.is_editable = True
            else:
                super()._compute_is_editable()

    @api.depends('budget_policy_id', 'company_id')
    def _compute_employee_journal_id(self):
        """Set the journal from the budget policy if available,
        otherwise use the company's default expense journal."""
        for sheet in self:
            if sheet.budget_policy_id and sheet.budget_policy_id.journal_id:
                sheet.employee_journal_id = sheet.budget_policy_id.journal_id
            else:
                sheet.employee_journal_id = super(HrExpenseSheet, sheet)._default_journal_id()

    def action_sheet_move_post(self):
        """
        Override action_sheet_move_post to add condition to check whether the
        remaining budget amount less than the total amount on Expenses and raise
        a warning if the amount is less than total budget amount. Also added
        condition to check whether the remaining budget amount less than 20% of
        total budget amount and send notification to discuss channel if condition
        met.
        """

        warning_messages, blocking_messages = self._get_sheet_level_warnings()
        if blocking_messages:
            return self._build_sheet_level_warning_action(blocking_messages)

        for sheet in self:
            if sheet.budget_policy_id and sheet.available_amount is not None:
                # Get total budget amount from budget policy
                total_budget = sheet.budget_policy_id.cap_amount or 0

                # Check if remaining budget is less than 20% of total budget
                if total_budget > 0 and sheet.available_amount <= (total_budget * 0.2):
                    sheet._send_budget_notification()

                # Determine comparable amount based on sheet type
                # Check if expense amount exceeds available budget
                total_to_compare = sheet.total_amount
                if sheet.advance_sheet_id:
                # If clearing an advance, only the amount exceeding the advance counts against remaining budget
                    clearing_amount = min(sheet.total_amount, sheet.advance_sheet_residual)
                    total_to_compare = sheet.total_amount - clearing_amount
                # else:
                #     total_to_compare = sheet.total_amount

                if total_to_compare > sheet.available_amount:
                    # if sheet.advance:
                    #     raise UserError(
                    #         _("Cannot post advance payment '%s': the requested amount (%.2f) "
                    #           "exceeds the available budget (%.2f). Budget is not sufficient.")
                    #         % (sheet.name, total_to_compare, sheet.available_amount)
                    #     )
                    raise UserError(
                        _("You don't have enough amount on your budget. Available: %.2f, Required: %.2f")
                        % (sheet.available_amount, total_to_compare)
                    )

        result = super(HrExpenseSheet, self).action_sheet_move_post()
        if warning_messages:
            return self._build_sheet_level_warning_action(
                warning_messages,
                result or self._get_default_next_action(),
            )
        return result

    def _send_budget_notification(self):
        """Send budget warning notification to relevant channels and users"""
        self.ensure_one()

        # Get budget responsibles - assuming this field exists similar to Odoo 13
        budget_responsibles = getattr(self, 'budget_reponsibles', self.env['res.users'])

        # Prepare notification message
        message = _(
            "The <a href=# data-oe-model=hr.expense.budget.policy data-oe-id=%d>%s</a> holds less than 20%% (%s) remaining budget on "
            "<a href=# data-oe-model=hr.expense.sheet data-oe-id=%d>%s</a>.") % (
                      self.budget_policy_id.id,
                      self.budget_policy_id.name or 'Budget Policy',
                      round(self.available_amount, 2),
                      self.id,
                      self.name
                  )

        # Send notifications to budget responsibles
        for user in budget_responsibles:
            if user.partner_id:
                # Send inbox notification
                notification_ids = [(0, 0, {
                    'res_partner_id': user.partner_id.id,
                    'notification_type': 'inbox'
                })]

                # Post message to user's channel
                ch = self.env['mail.channel'].channel_get([user.partner_id.id])
                if ch and ch.get("id"):
                    ch_obj = self.env['mail.channel'].browse(ch["id"])
                    ch_obj.message_post(
                        body=message,
                        message_type='comment',
                        subtype='mail.mt_comment',
                    )

                # Post notification
                self.message_post(
                    author_id=self.env.user.partner_id.id,
                    body=message,
                    message_type='notification',
                    subtype='mail.mt_comment',
                    notification_ids=notification_ids,
                    partner_ids=[user.partner_id.id],
                )