from odoo import models, fields


class CustomProductTemplate(models.Model):
    _inherit = "product.template"

    is_technical_product = fields.Boolean(string="Is Technical Product",
                                          help="Specify whether the product can be selected in an Contract.")
    partner_id = fields.Many2one('res.partner', string="Supplier")
    modality = fields.Many2one('contract.modality', string="Modality")
