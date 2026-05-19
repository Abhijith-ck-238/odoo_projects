from odoo import models, fields, api
import re


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    compressed_name = fields.Char('Compressed Product Name', compute='compute_compressed_name', store=True,
                                  default='')

    @api.depends('name')
    def compute_compressed_name(self):
        for rec in self:
            name = rec.remove(rec.name)
            rec.compressed_name = name

    def remove(self, string):
        if string:
            pattern = re.compile(r'\s+')
            return re.sub(pattern, '', string)
        else:
            return ''

    def set_compressed_product_name(self):
        pname = self.env['product.template'].search([('compressed_name', '=', False)])
        for rec in pname:
            if rec.name:
                name = rec.remove(rec.name)
                rec.write({'compressed_name': name})
            else:
                pass
