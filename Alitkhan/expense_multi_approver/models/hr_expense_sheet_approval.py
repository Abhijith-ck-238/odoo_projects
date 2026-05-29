from odoo import models, fields

class HrExpenseSheetAprovals(models.Model):
    _name = "hr.expense.sheet.approval"
    _order = "sequence"

    sequence = fields.Integer("Sequence")
    user_id = fields.Many2one("res.users", "Employee", required=True, readonly=True)
    approved_by = fields.Many2one("res.users", readonly=True)
    sheet_id = fields.Many2one("hr.expense.sheet", readonly=True, ondelete="cascade")
    approved = fields.Boolean(readonly=True)
    approved_date = fields.Datetime("Approved Date", readonly=True)
    