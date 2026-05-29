# -*- coding: utf-8 -*-
from odoo import models, fields, api


class HrExpenseBudgetConsumption(models.Model):
    _name = 'hr.expense.budget.consumption'
    _description = 'Expense Budget Consumption'
    _order = 'period_key desc'
    _inherit = ['mail.thread', 'mail.activity.mixin']


    policy_id = fields.Many2one(
        'hr.expense.budget.policy',
        string='Budget Policy',
        required=True,
        ondelete='cascade',
        index=True
    )
    period_key = fields.Char(
        string='Period',
        index=True,
        help='Period identifier (e.g., 2025-11, 2025-Q4, 2025)'
    )
    currency_id = fields.Many2one(
        'res.currency',
        related='policy_id.currency_id',
        string='Currency',
        store=True,
        readonly=True
    )

    # Consumption Amounts
    consumed_amount = fields.Monetary(
        string='Consumed Amount',
        currency_field='currency_id',
        default=0.0,
        help='Total approved/posted expenses',
        tracking=True
    )
    committed_amount = fields.Monetary(
        string='Committed Amount',
        currency_field='currency_id',
        default=0.0,
        compute='_compute_committed_amount',
        help='Paid advances not yet cleared',
        store=True,
        tracking=True

    )
    available_amount = fields.Monetary(
        string='Available Amount',
        currency_field='currency_id',
        compute='_compute_available_amount',
        store=True,
        tracking=True
    )

    cap_amount = fields.Monetary(
        related='policy_id.cap_amount',
        string='Cap Amount',
        currency_field='currency_id',
        store=True,
        readonly=True,
        tracking=True
    )

    consumption_percentage = fields.Float(
        string='Consumption %',
        store=True
    )


    # @api.depends('policy_id.expense_sheet_ids', 'policy_id.expense_sheet_ids.total_amount',
    #              'policy_id.expense_sheet_ids.state')
    # def _compute_committed_amount(self):
    #     for record in self:
    #         committed_total = 0.0
    #         if record.policy_id:
    #             sheets = self.env['hr.expense.sheet'].search([
    #                 ('budget_policy_id', '=', record.policy_id.id),
    #                 ('state', 'in', ['post', 'done'])
    #             ])
    #             committed_total = sum(sheets.mapped('total_amount'))
    #         record.committed_amount = committed_total

    @api.depends('policy_id.expense_sheet_ids',
                 'policy_id.expense_sheet_ids.total_amount',
                 'policy_id.expense_sheet_ids.state',
                 'policy_id.expense_sheet_ids.advance_sheet_id')
    def _compute_committed_amount(self):
        """
        Calculate committed amount considering:
        - Normal expenses: Subtract from available (positive contribution)
        - Clearing sheets: Add back to available (negative contribution)
        """
        for record in self:
            committed_total = 0.0
            if record.policy_id:
                sheets = self.env['hr.expense.sheet'].search([
                    ('budget_policy_id', '=', record.policy_id.id),
                    ('state', 'in', ['post', 'done'])
                ])
                print("sheets",sheets)

                for sheet in sheets:
                    # Check if this is a clearing sheet
                    if sheet.advance_sheet_id:
                        # Clearing sheet: SUBTRACT from committed (adds to available)
                        committed_total -= sheet.advance_sheet_residual
                        print("committed_total",committed_total)
                    else:
                        # Normal expense or advance: ADD to committed (reduces available)
                        committed_total += sheet.total_amount
                        print("committed_total",committed_total)

            record.committed_amount = committed_total
            print("record.committed_amount",record.committed_amount)


    @api.depends('cap_amount','committed_amount')
    def _compute_available_amount(self):
        print("_compute_available_amount-------")
        for record in self:
            record.available_amount = record.cap_amount - record.committed_amount

    _sql_constraints = [
        ('policy_period_uniq', 'UNIQUE(policy_id, period_key)',
         'Only one consumption record per policy and period!')
    ]
