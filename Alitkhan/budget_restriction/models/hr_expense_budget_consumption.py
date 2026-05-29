# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class HrExpenseBudgetConsumption(models.Model):
    _name = 'hr.expense.budget.consumption'
    _description = 'Expense Budget Consumption'
    _order = 'period_key desc'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'policy_id'


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
    threshold_notified = fields.Boolean(
        string='80% Threshold Notified',
        default=False,
        copy=False,  # Don't carry over when duplicating the record
        help="Set to True once the 80% consumption notification has been sent. "
             "Resets automatically when consumption drops below 80%.",
    )

    @api.depends(
        'policy_id.expense_sheet_ids',
        'policy_id.expense_sheet_ids.total_amount',
        'policy_id.expense_sheet_ids.state',
        'policy_id.expense_sheet_ids.advance_sheet_id',
        'policy_id.expense_sheet_ids.clearing_residual',
        'policy_id.expense_sheet_ids.payment_return_ids.state',
        'policy_id.expense_sheet_ids.payment_return_ids.amount',
    )
    def _compute_committed_amount(self):
        for record in self:
            if not record.policy_id:
                record.committed_amount = 0.0
                continue

            committed = 0.0
            sheets = self.env['hr.expense.sheet'].search([
                ('budget_policy_id', '=', record.policy_id.id),
                ('state', 'in', ['post', 'done'])
            ])

            for sheet in sheets:
                if sheet.advance:
                    # Advance sheet → commitment is its remaining residual
                    committed += sheet.clearing_residual
                else:
                    if sheet.advance_sheet_id:
                        # Clearing expenses are only counted when the corresponding advance is fully cleared
                        if sheet.advance_sheet_residual <= 0.0:
                            committed += sheet.total_amount
                    else:
                        # Normal expense
                        committed += sheet.total_amount

                # Advance returns: employee returned cash → re-commit that amount
                for payment in sheet.payment_return_ids:
                    if payment.state in ('posted', 'reconciled') and payment.payment_type == 'inbound':
                        committed += payment.amount

            record.committed_amount = committed

            # Consumption percentage : calculating % of cap amount within committed amount
            if record.cap_amount > 0:
                percentage = (record.committed_amount / record.cap_amount) * 100
            else:
                percentage = 0.0

            record.consumption_percentage = percentage

            # Threshold notification logic
            if percentage >= 80.0:
                if not record.threshold_notified:
                    record._send_budget_threshold_notification()
                    record.threshold_notified = True
            else:
                record.threshold_notified = False

    def _send_budget_threshold_notification(self):
        """Send notification when budget reaches 80% consumption"""
        self.ensure_one()

        # Send notification to Budget Owner
        if self.policy_id.budget_owner_id:
            template = self.env.ref('custom_expense.mail_template_budget_notification_1', raise_if_not_found=False)
            if template:
                base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
                ctx = {
                    'subject': 'Budget Alert: 80%% Threshold Reached - %s' % self.policy_id.name,
                    'email_to': self.policy_id.budget_owner_id.partner_id.email or '',
                    'namee': self.policy_id.budget_owner_id.name,
                    'company_name': self.env.company.name,
                    'message': 'The budget policy "%s" has reached %.2f%% consumption. Committed Amount: %s %s of Cap Amount: %s %s.' % (
                    self.policy_id.name,
                    self.consumption_percentage,
                    self.committed_amount,
                    self.currency_id.symbol,
                    self.cap_amount,
                    self.currency_id.symbol
                ),
                    'url': '%s/web#id=%s&model=hr.expense.budget.policy&view_type=form' % (
                        base_url, self.policy_id.id
                    ),
                }
                template.with_context(ctx).send_mail(self.policy_id.id, force_send=True)

    @api.depends('cap_amount','committed_amount')
    def _compute_available_amount(self):
        for record in self:
            record.available_amount = record.cap_amount - record.committed_amount

    def action_view_expense_sheets(self):
        """Open list of expense sheets contributing to committed amount"""
        self.ensure_one()
        return {
            'name': 'Committed Expense Sheets',
            'type': 'ir.actions.act_window',
            'res_model': 'hr.expense.sheet',
            'view_mode': 'list,form',
            'domain': [
                ('budget_policy_id', '=', self.policy_id.id),
                ('state', 'in', ['post', 'done'])
            ],
            'context': {
                'default_budget_policy_id': self.policy_id.id,
            }
        }

    @api.constrains('policy_id')
    def _check_unique_policy(self):
        for record in self:
            if self.search_count([
                ('policy_id', '=', record.policy_id.id),
                ('id', '!=', record.id)
            ]) > 0:
                raise ValidationError(
                    _('A Budget Consumption already exists for this Budget Policy.')
                )
