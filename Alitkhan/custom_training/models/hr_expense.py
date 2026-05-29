from odoo import fields, models

class HrExpense(models.Model):
    _inherit = 'hr.expense.sheet'

    training_id = fields.Many2one('training.ticket', "Training")
