from odoo import models, fields, api, _
from odoo.exceptions import UserError

class ProductProduct(models.Model):
    _inherit = "product.product"

    # This function is to help with data import proccess, so we can upload the products just by using reference code
    # @Mohammed Saeb
    @api.model
    def name_search(self, name='', args=None, operator="ilike", limit=100):
        args = args or []
        domain = args + ['|', ('name', operator, name), ('default_code', 'ilike', name)]
        products = self.search(domain, limit=limit)
        return [(product.id, f"[{product.default_code}] {product.name}" if product.default_code else product.name) for product
         in products]
