from odoo import models, fields


class AccountMove(models.Model):
    _inherit = 'account.move'

    expense_sheet_id = fields.Many2one('hr.expense.sheet',
                                       string="Expense Report")
