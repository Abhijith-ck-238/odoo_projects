from odoo import models, fields, api

class AccountMove(models.Model):
    _inherit = "account.move"

    company_report_id = fields.Many2one('res.company', string="Company Report", default=lambda self: self.env.company)
    