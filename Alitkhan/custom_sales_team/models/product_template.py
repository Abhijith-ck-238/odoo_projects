from odoo import models, fields, api


class ExtendProductTemplate(models.Model):
    _inherit = 'product.template'

    is_duplicate_internal_reference = fields.Boolean(default=False)
    is_duplicate_name = fields.Boolean(default=False)
    product_variant_id = fields.Many2one('product.product', 'Product', compute='_compute_product_variant_id',
                                         store=True)

    def _get_default_category_id(self):
        category = self.env['product.category'].search([('name', '=', 'All')], limit=1)
        if category:
            return category.id
        else:
            pass

    categ_id = fields.Many2one(
        'product.category', 'Product Category',
        change_default=True, default=_get_default_category_id, group_expand='_read_group_categ_id',
        required=True, help="Select category for the current product")

    def find_duplicate_internal_reference(self):
        templates = self.env['product.template'].search([('default_code', '!=', False)])
        reference = templates.mapped('default_code')
        duplicate_list = {i: reference.count(i) for i in reference if reference.count(i) > 1}.keys()
        for rec in duplicate_list:
            product_templates = self.env['product.template'].search([('default_code', '=', rec)])
            for product in product_templates:
                product.is_duplicate_internal_reference = True

    def find_duplicate_names(self):
        products = self.env['product.template'].search([('name', '!=', False)])
        name_list = products.mapped('name')
        duplicates = [name for name, count in Counter(name_list).items() if count > 1]
        for name in duplicates:
            recs = self.env['product.template'].search([('name', '=', name)])
            recs.write({'is_duplicate_name': True})
