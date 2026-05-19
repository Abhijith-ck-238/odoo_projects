from odoo import models, fields, api


class ConfigWizard(models.TransientModel):
    _name = "config.wizard"
    _description = 'Config wizard'

    description = fields.Char(string="Description", readonly=True)
    product_lines = fields.One2many("config.wizard.line", "conn", string="Product Lines",readonly=True)


class ConfigWizardLine(models.TransientModel):
    _name = "config.wizard.line"
    _description = 'Config wizard Line'

    conn = fields.Integer()
    product_id = fields.Many2one('product.product', string="Product")
    qty = fields.Integer(string="Quantity")
