from odoo import models, fields


class CustomCrossoveredBudgetLines(models.Model):
    _inherit = 'budget.line'

    amount_to_extend = fields.Float(string="Amount to Extend")
    achieved_amount = fields.Monetary(
        compute='_compute_all',
        string='Achieved',
        help="Amount Billed/Invoiced.",store=True)
    achieved_percentage = fields.Float(
        compute='_compute_all',
        string='Achieved (%)',store=True)
    committed_amount = fields.Monetary(
        compute='_compute_all',
        string='Committed',
        help="Already Billed amount + Confirmed purchase orders.",store=True)
    committed_percentage = fields.Float(
        compute='_compute_all',
        string='Committed (%)',store=True)

