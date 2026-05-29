# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class HrExpenseBudgetPolicy(models.Model):
    _name = 'hr.expense.budget.policy'
    _description = 'Expense Budget Policy'
    _order = 'name'
    _inherit = ['mail.thread', 'mail.activity.mixin']


    name = fields.Char(
        string='Policy Name',
        required=True,
        tracking=True,
        index=True
    )
    company_id = fields.Many2one(
        'res.company',
        string='Company',
        required=True,
        default=lambda self: self.env.company,
        tracking=True
    )

    # Scope Dimensions
    scope_employee_ids = fields.Many2many(
        'hr.employee',
        'budget_policy_employee_rel',
        'policy_id',
        'employee_id',
        string='Employees',
        tracking=True
    )
    scope_analytic_plan_ids = fields.Many2many(
        'account.analytic.plan',
        'budget_policy_plan_rel',
        'policy_id',
        'analytic_id',
        string='Analytic plan',
        tracking=True
    )
    scope_analytic_account_ids = fields.Many2many(
        'account.analytic.account',
        'budget_policy_analytic_rel',
        'policy_id',
        'analytic_id',
        string='Analytic Accounts',
        tracking=True
    )

    scope_product_ids = fields.Many2many(
        'product.product',
        'budget_policy_product_rel',
        'policy_id',
        'product_id',
        string='Products',
        tracking=True
    )
    scope_tag_ids = fields.Many2many(
        'budget.policy.tag',
        'budget_policy_tag_rel',  # Relation table name
        'policy_id',  # Column in relation table for this model
        'tag_id',  # Column in relation table for tag
        string='Tags'
    )

    # Time Bucket Configuration
    time_bucket = fields.Selection([
        ('monthly', 'Monthly'),
        ('quarterly', 'Quarterly'),
        ('yearly', 'Yearly'),
        ('custom', 'Custom Date Range')
    ], string='Time Bucket', required=True, default='monthly', tracking=True)

    custom_date_from = fields.Date(
        string='Custom Start Date',
        tracking=True
    )
    custom_date_to = fields.Date(
        string='Custom End Date',
        tracking=True
    )

    # Budget Configuration
    currency_id = fields.Many2one(
        'res.currency',
        string='Policy Currency',
        required=True,
        default=lambda self: self.env.company.currency_id,
        tracking=True
    )
    cap_amount = fields.Monetary(
        string='Cap Amount',
        currency_field='currency_id',
        required=True,
        tracking=True
    )

    # Behavior Configuration
    behavior = fields.Selection([
        ('hard_stop', 'Hard Stop (Block Submission/Approval)'),
        ('soft_warn', 'Soft Warn (Allow with Budget Owner Approval)')
    ], string='Behavior', required=True, default='soft_warn', tracking=True)

    count_advances = fields.Boolean(
        string='Count Committed Advances',
        default=True,
        help='Include paid but not cleared advance payment requests in consumption',
        tracking=True
    )

    budget_owner_id = fields.Many2one(
        'res.users',
        string='Budget Owner',
        required=True,
        tracking=True
    )

    grace_percentage = fields.Float(
        string='Grace %',
        default=0.0,
        help='Tolerance percentage before triggering warn/stop',
        tracking=True
    )

    # Effective Period
    effective_from = fields.Date(
        string='Effective From',
        required=True,
        default=fields.Date.today,
        tracking=True
    )
    effective_to = fields.Date(
        string='Effective To',
        tracking=True
    )

    # Consumption Lines
    consumption_ids = fields.One2many(
        'hr.expense.budget.consumption',
        'policy_id',
        string='Budget Consumption'
    )

    expense_sheet_ids = fields.One2many(
        'hr.expense.sheet',
        'budget_policy_id',
        string="Expense Sheets"
    )


    @api.constrains('effective_from', 'effective_to')
    def _check_effective_dates(self):
        """Validate effective period dates"""
        for policy in self:
            if policy.effective_to and policy.effective_from > policy.effective_to:
                raise ValidationError(_('Effective From date must be before Effective To date.'))

    @api.constrains('grace_percentage')
    def _check_grace_percentage(self):
        """Validate grace percentage is within valid range"""
        for policy in self:
            if policy.grace_percentage < 0 or policy.grace_percentage > 100:
                raise ValidationError(_('Grace percentage must be between 0 and 100.'))

    @api.constrains('cap_amount')
    def _check_cap_amount(self):
        """Validate cap amount is positive"""
        for policy in self:
            if policy.cap_amount <= 0:
                raise ValidationError(_('Cap amount must be positive.'))

    def _get_period_key(self, expense_date):
        """
        Generate period key based on time bucket configuration
        Returns: string like '2025-11', '2025-Q4', '2025', or 'custom'
        """
        self.ensure_one()

        if self.time_bucket == 'monthly':
            return expense_date.strftime('%Y-%m')
        elif self.time_bucket == 'quarterly':
            quarter = (expense_date.month - 1) // 3 + 1
            return f"{expense_date.year}-Q{quarter}"
        elif self.time_bucket == 'yearly':
            return str(expense_date.year)
        elif self.time_bucket == 'custom':
            return 'custom'

        return False
