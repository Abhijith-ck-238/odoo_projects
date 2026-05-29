from odoo import fields, models, api


class ProductLines(models.Model):
    _name = 'sp.order.product.lines'
    _description = 'Product Lines'

    product_id = fields.Many2one('product.product', 'Product', tracking=True)
    quantity = fields.Float("Quantity", tracking=True)
    sp_order_id = fields.Many2one('sp.order')

    @api.model
    def write(self, vals):
        if vals.get('quantity'):
            message = "Quantity:" + str( self.quantity) + " --> " + str(vals.get('quantity'))
            self.sp_order_id.message_post(body=message)
        if vals.get('product_id'):
            product = self.env['product.product'].browse(vals.get('product_id'))
            message = "Product:" + str(self.product_id.name) + " --> " + str(product.name)
            self.sp_order_id.message_post(body=message)

        return super(ProductLines, self).write(vals)
