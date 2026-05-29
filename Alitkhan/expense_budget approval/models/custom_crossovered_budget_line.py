from odoo import models, fields


class CustomCrossoveredBudgetLines(models.Model):
    _inherit = 'budget.line'

    amount_to_extend = fields.Float(string="Amount to Extend")
    paid_date = fields.Date("Paid Date")
    crossovered_budget_id = fields.Many2one('budget.analytic',string="Budget")
    practical_amount = fields.Monetary("Practical Amount")
    percentage = fields.Float("Achievement")
    planned_amount = fields.Monetary("Planned Amount")
    analytic_account_id = fields.Many2one('account.analytic.account',string="Budget")
