from odoo import models, fields


class CrmLead(models.Model):
    _inherit = 'crm.lead'

    sale_order_ids = fields.Many2many('sale.order')
