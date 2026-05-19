# -*- coding: utf-8 -*-
from dateutil.relativedelta import relativedelta
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from datetime import date


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

    analytic_distribution = fields.Json(
        'Analytic Distribution',
        store=True, copy=True, readonly=False,
    )
    analytic_precision = fields.Integer(
        store=False,
        default=lambda self: self.env['decimal.precision'].precision_get("Percentage Analytic"),
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

    bucket_amount = fields.Float('Bucket Amount', tracking=True)

    last_bucket_date = fields.Date(
        string="Last Bucket Applied",
        help="Tracks the last date the bucket amount was applied",
    )

    journal_id = fields.Many2one(
        'account.journal', string="Journal", store=True, readonly=False)

    budget_consumption_id = fields.Many2one('hr.expense.budget.consumption', string='Budget Consumption')

    state = fields.Selection(
        [
            ('open', 'Open'),
            ('achieved', 'Achieved'),
            ('closed', 'Closed'),
        ],
        string='Status',
        default='open',
        tracking=True,
        copy=False
    )

    active = fields.Boolean(default=True, tracking=True)

    available_amount = fields.Monetary(related='consumption_ids.available_amount',
        string='Available Amount',
        currency_field='currency_id',
        store=True,
        tracking=True
    )

    consumption_percentage = fields.Float(related='consumption_ids.consumption_percentage',
        string='Consumption %',
        store=True
    )

    analytic_distribution_display = fields.Char(
        string='Analytic Distribution (Names)',
        compute='_compute_analytic_distribution_display'
    )

    @api.constrains('effective_from', 'effective_to')
    def _check_effective_dates(self):
        """Validate effective period dates"""
        for policy in self:
            if policy.effective_to and policy.effective_from > policy.effective_to:
                raise ValidationError(_('Effective From date must be before Effective To date.'))
    
    @api.onchange('scope_analytic_plan_ids')
    def _onchange_scope_analytic_plan_ids(self):
        """
        Remove analytic distribution entries that do not belong
          to the selected analytic plans.
        """
        for record in self:
            # If there is no analytic distribution, nothing to clean
            if not record.analytic_distribution:
                continue

            # Get selected analytic plan IDs
            selected_plan_ids = set(record.scope_analytic_plan_ids.ids)

            # Prepare a new cleaned distribution
            distribution = {}

            # Loop through current analytic distribution
            for account_id_str, percentage in record.analytic_distribution.items():
                account_id = int(account_id_str)
                account = self.env['account.analytic.account'].browse(account_id)

                # Keep only accounts that belong to selected plans
                if account.exists() and account.root_plan_id.id in selected_plan_ids:
                    distribution[account_id_str] = percentage

            # Replace old distribution with the cleaned one
            record.analytic_distribution = distribution

    @api.model
    def _post_renewal_message(self, policy, old_cap):
        """Post a message about budget renewal"""
        policy.message_post(
            body=_(
                'Budget auto-renewed: Cap updated from %s → %s (added %s)'
            ) % (
                     old_cap,
                     policy.cap_amount,
                     policy.bucket_amount
                 ),
            subject=_('Budget Auto-Renewal')
        )

    @api.model
    def _cron_update_budget_cap(self):
        """
        Cron job to automatically renew budgets based on time bucket.
        Increases cap_amount by bucket_amount for each period that has elapsed.
        """
        today = fields.Date.today()
        renewed_count = 0

        # Fetch policies eligible for renewal
        policies = self.search([
            ('bucket_amount', '>', 0),
            ('time_bucket', 'in', ['monthly', 'quarterly', 'yearly']),
            ('effective_from', '<=', today),
            '|',
            ('effective_to', '=', False),
            ('effective_to', '>=', today),
        ])

        for policy in policies:
            start = policy.effective_from
            end = min(policy.effective_to or today, today)

            if not start or end < start:
                continue

            # Count completed periods since effective_from
            periods = 0
            current = start
            year_list = []
            month_list = []
            q_year_list = []
            while True:
                if policy.time_bucket == 'monthly':
                    next_date = current + relativedelta(months=1)
                    next_date = date(next_date.year, next_date.month, 1)
                elif policy.time_bucket == 'quarterly':
                    next_date = current + relativedelta(months=3)
                    next_date = date(next_date.year, next_date.month, 1)
                elif policy.time_bucket == 'yearly':
                    next_date = current + relativedelta(years=1)
                    next_date = date(next_date.year, 1, 1)
                else:
                    break

                if next_date <= end:  # Changed from < to <= to include end date
                    periods += 1
                    current = next_date

                    # Append AFTER validation
                    if policy.time_bucket == 'monthly':
                        month_list.append(next_date)
                    elif policy.time_bucket == 'quarterly':
                        q_year_list.append(next_date)
                    elif policy.time_bucket == 'yearly':
                        year_list.append(next_date)
                else:
                    break

            # Only increase if periods have elapsed
            if periods > 0:
                total_increase = policy.bucket_amount 
                old_cap = policy.cap_amount
                if policy.time_bucket == 'yearly':
                    # Check if today is the first day of the year (January 1st)
                    is_first_day_of_year = today.day == 1 and today.month == 1

                    # Check if current year is in year_list (only year matters, not day/month)
                    current_year = today.year
                    is_in_year_list = any(dt.year == current_year for dt in year_list)

                    if is_first_day_of_year and is_in_year_list:
                        policy.cap_amount += policy.bucket_amount
                        self._post_renewal_message(policy, old_cap)
                elif policy.time_bucket == 'monthly':
                    # Check if today is the first day of the month
                    is_first_day = today.day == 1

                    # Check if current month and year are in month_list (only month/year matter, not day)
                    current_month = today.month
                    current_year = today.year
                    is_in_month_list = any(
                        dt.month == current_month and dt.year == current_year for dt in month_list)

                    if is_first_day and is_in_month_list:
                        policy.cap_amount += policy.bucket_amount
                        self._post_renewal_message(policy, old_cap)
                elif policy.time_bucket == 'quarterly':
                    # Check if today is the first day of the month
                    is_first_day = today.day == 1

                    # Check if current month and year are in q_year_list (only month/year matter, not day)
                    current_month = today.month
                    current_year = today.year
                    is_in_quarterly_list = any(
                        dt.month == current_month and dt.year == current_year for dt in q_year_list)

                    if is_first_day and is_in_quarterly_list:
                        policy.cap_amount += policy.bucket_amount
                        self._post_renewal_message(policy, old_cap)
                else :
                    policy.cap_amount += total_increase
                    self._post_renewal_message(policy, old_cap)
                renewed_count += 1

        return renewed_count

    def _send_budget_owner_notification(self, is_change=False):
        """Send email notification to Budget Owner"""
        self.ensure_one()
        template = self.env.ref('custom_expense.mail_template_budget_notification_1', raise_if_not_found=False)
        if template:
            # Prepare context with required variables
            base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')

            # Different message based on whether it's a new assignment or change
            if is_change:
                message = 'You have been assigned as the new Budget Owner for the budget policy: %s.' % self.name
                subject = 'Budget Owner Changed: %s' % self.name
            else:
                message = 'You have been assigned as the Budget Owner for the budget policy: %s.' % self.name
                subject = 'Budget Policy: %s' % self.name

            ctx = {
                'subject': subject,
                'email_to': self.budget_owner_id.partner_id.email or '',
                'email_from': self.company_id.email or self.env.company.email,
                'namee': self.budget_owner_id.name,
                'message': message,
                'url': '%s/web#id=%s&model=hr.expense.budget.policy&view_type=form' % (base_url, self.id),
                'company_name': self.company_id.name or self.env.company.name,

            }
            template.with_context(ctx).send_mail(self.id, force_send=True)

    @api.model
    def create(self, vals):
        """When creating a Budget Policy, it should automatically create a Budget Consumption."""
        policy = super(HrExpenseBudgetPolicy, self).create(vals)
        self.env['hr.expense.budget.consumption'].create({
            'policy_id': policy.id
        })

        if policy.budget_owner_id:
            policy._send_budget_owner_notification()

        return policy

    def write(self, vals):
        """Send notification when Budget Owner is changed"""
        # Check if budget_owner_id is being changed
        if 'budget_owner_id' in vals:
            for record in self:
                # Store old owner to check if it's actually changing
                old_owner_id = record.budget_owner_id.id if record.budget_owner_id else False
                new_owner_id = vals.get('budget_owner_id')

                # Only send notification if owner is actually changing and new owner exists
                if old_owner_id != new_owner_id and new_owner_id:
                    # Call parent write first to update the record
                    res = super(HrExpenseBudgetPolicy, record).write(vals)
                    # Send notification to new owner
                    record._send_budget_owner_notification(is_change=True)
                    return res

        # Normal write for other field changes
        return super(HrExpenseBudgetPolicy, self).write(vals)

    def _compute_analytic_distribution_display(self):
        for record in self:
            if not record.analytic_distribution:
                record.analytic_distribution_display = ''
                continue
            parts = []
            for account_id_str, percentage in record.analytic_distribution.items():
                account = self.env['account.analytic.account'].browse(int(account_id_str))
                if account.exists():
                    parts.append('%s: %s%%' % (account.name, percentage))
                else:
                    parts.append('Unknown (%s): %s%%' % (account_id_str, percentage))
            record.analytic_distribution_display = ', '.join(parts)
