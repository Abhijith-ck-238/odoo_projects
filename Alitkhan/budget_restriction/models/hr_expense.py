# -*- coding: utf-8 -*-
from odoo import models, fields, api

class HrExpense(models.Model):
    _inherit = 'hr.expense'

    budget_policy_id = fields.Many2one(
        'hr.expense.budget.policy',
        related='sheet_id.budget_policy_id',
        store=True,
        string='Budget Policy'
    )

    analytic_account_ids = fields.Many2many(
        'account.analytic.account',
        relation='hr_expense_analytic_account_rel',
        column1='expense_id',
        column2='account_id',
        string='Analytic Accounts',
        context={'active_test': False}
    )

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('analytic_distribution'):
                account_ids = {
                    int(sub_k.strip())
                    for key in vals['analytic_distribution'].keys()
                    for sub_k in key.split(',')
                    if sub_k.strip().isdigit()
                }
                if account_ids:
                    vals['analytic_account_ids'] = [(6, 0, list(account_ids))]
        return super(HrExpense, self).create(vals_list)

    def write(self, vals):
        res = super(HrExpense, self).write(vals)
        if 'analytic_distribution' in vals:
            for record in self:
                distribution = record.analytic_distribution or {}
                account_ids = {
                    int(sub_k.strip())
                    for key in distribution.keys()
                    for sub_k in key.split(',')
                    if sub_k.strip().isdigit()
                }
                # Using sudo().with_context(active_test=False) ensures we can write inactive ids if needed natively, though (6,0) bypasses most checks.
                record.analytic_account_ids = [(6, 0, list(account_ids))] if account_ids else [(5, 0, 0)]
        return res

    @api.model
    def action_sync_analytic_account_ids(self):
        # Fast SQL script to populate existing older records instantly. Triggers from the Server Action.
        self.env.cr.execute("""
            INSERT INTO hr_expense_analytic_account_rel (expense_id, account_id)
            SELECT DISTINCT e.id, CAST(sub_key AS INTEGER)
            FROM hr_expense e
            CROSS JOIN jsonb_object_keys(e.analytic_distribution) AS key
            CROSS JOIN unnest(string_to_array(key, ',')) AS sub_key
            JOIN account_analytic_account a ON a.id = CAST(sub_key AS INTEGER)
            WHERE e.analytic_distribution IS NOT NULL 
              AND sub_key ~ '^[0-9]+$'
            EXCEPT
            SELECT expense_id, account_id FROM hr_expense_analytic_account_rel;
        """)
