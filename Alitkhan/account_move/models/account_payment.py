from odoo import fields, models


class AccountPayment(models.Model):
    _inherit = "account.payment"

    expense_id = fields.Many2one('hr.expense')
