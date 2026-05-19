from odoo import models, fields, api, _
from odoo.exceptions import UserError


class Product_template_ext(models.Model):
    _inherit="product.template"

    product_long_desc = fields.Text(string="Product Long Description")