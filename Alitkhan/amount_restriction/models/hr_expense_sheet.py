# -*- coding: utf-8 -*-

from odoo import models, fields, api , _
from odoo.exceptions import ValidationError


class HrExpenseSheet(models.Model):
    _inherit = 'hr.expense.sheet'

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
    #
    # @api.depends('budget_policy_id')
    # def _compute_available_amount(self):
    #     print("_compute_available_amount::")
    #     for rec in self:
    #         if not rec.budget_policy_id:
    #             rec.available_amount = 0.0
    #             continue
    #
    #         available = self.env['hr.expense.budget.consumption'].search([
    #             ('policy_id', '=', rec.budget_policy_id.id)
    #         ], limit=1)
    #
    #         rec.available_amount = available.available_amount if available else 0.0

    @api.model
    def write(self, vals):
        res = super(HrExpenseSheet, self).write(vals)

        for sheet in self:
            policy = sheet.budget_policy_id

            # If the policy is removed → clear distribution
            if not policy:
                if sheet.expense_line_ids:
                    sheet.expense_line_ids.write({'analytic_distribution': False})
                continue

            analytic_accounts = policy.scope_analytic_account_ids

            # If no analytic accounts → clear distribution
            if not analytic_accounts:
                sheet.expense_line_ids.write({'analytic_distribution': False})
                continue

            # Build equal percentage distribution
            percentage = 100.0 / len(analytic_accounts)
            distribution = {str(acc.id): percentage for acc in analytic_accounts}

            # Update all expense lines
            if sheet.expense_line_ids:
                sheet.expense_line_ids.write({'analytic_distribution': distribution})

        return res


    def action_submit_sheet(self):
        for sheet in self:
            if sheet.available_amount > 0 and sheet.total_amount > sheet.available_amount:
                raise ValidationError(
                    _("Total expense (%.2f) cannot be more than the available amount (%.2f).")
                    % (sheet.total_amount, sheet.available_amount)
                )

        return super(HrExpenseSheet, self).action_submit_sheet()
