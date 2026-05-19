from odoo import models, api


class AnalyticAccount(models.Model):
    _inherit = "hr.expense.sheet"

    @api.onchange('analytic_account_id')
    def _onchange_analytic_account_id(self):
        self.journal_id = self.analytic_account_id.journal_id.id
