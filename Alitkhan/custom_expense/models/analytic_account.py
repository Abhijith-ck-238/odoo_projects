from odoo import models, fields


class AnalyticAccount(models.Model):
    _inherit = "account.analytic.account"

    journal_id = fields.Many2one('account.journal', "Expense Journal")
