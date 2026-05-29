from odoo import models, fields, api


class CustomSalesTeam(models.Model):
    _inherit = 'crm.team'

    default_warehouse_id = fields.Many2one('stock.warehouse', string="Warehouse")
