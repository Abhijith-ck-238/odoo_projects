from odoo import fields, models

class AccountMove(models.Model):
    _inherit = 'account.move'

    is_direct_sales = fields.Boolean(string="Direct Sales")
    is_financial_instrument = fields.Boolean(string="F.I (Financial Instrument)")
