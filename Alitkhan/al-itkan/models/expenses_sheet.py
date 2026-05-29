from odoo import models, fields, api
from odoo.exceptions import UserError

class HrExpenses(models.Model):
    _inherit = "hr.expense"
    
    product_id = fields.Many2one(states={'draft': [('readonly', False)], 'reported': [('readonly', False)], 'approved': [('readonly', False)], 'refused': [('readonly', False)]})
    analytic_account_id = fields.Many2one("account.analytic.account", string="Budget")

class HrExpensesSheet(models.Model):
    _inherit = "hr.expense.sheet"

    analytic_account_id = fields.Many2one("account.analytic.account", string="Budget")
    expense_line_ids = fields.One2many(states={'done': [('readonly', True)], 'post': [('readonly', True)]})

    # This is the original Function
    @api.constrains("analytic_account_id", "expense_line_ids")
    def _get_analytic_account(self):
        for report in self:
            for line in report.expense_line_ids:
                line.analytic_account_id = report.analytic_account_id.id
