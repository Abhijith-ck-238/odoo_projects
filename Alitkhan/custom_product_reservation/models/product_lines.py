from odoo import fields, models, api
from odoo.exceptions import ValidationError


class ProductLines(models.Model):
    _name = 'product.lines'
    _description = 'Product Lines'

    product_id = fields.Many2one('product.product', 'Product', tracking=True)
    quantity = fields.Float("Quantity",default=1,tracking=True)
    reservation_id = fields.Many2one('product.reservation')
    return_quantity = fields.Float("Return Quantity", tracking=True)
    used_quantity = fields.Float("Used Quantity")

    @api.model
    def write(self, vals):
        if vals.get('quantity'):
            message = "Quantity:" + str( self.quantity) + " --> " + str(vals.get('quantity'))
            self.reservation_id.message_post(body=message)
        if vals.get('product_id'):
            product = self.env['product.product'].browse(vals.get('product_id'))
            message = "Product:" + str(self.product_id.name) + " --> " + str(product.name)
            self.reservation_id.message_post(body=message)
        if vals.get('return_quantity'):
            message = "Return Quantity:" + str(self.return_quantity) + " --> " + str(vals.get('return_quantity'))
            self.reservation_id.message_post(body=message)

        return super(ProductLines, self).write(vals)

    @api.onchange('quantity', 'return_quantity')
    def onchange_quantity_and_return_quantity(self):
        for rec in self:
            rec.used_quantity = rec.quantity - rec.return_quantity

    @api.constrains('quantity')
    def _check_quantity_positive(self):
        for record in self:
            if record.quantity <= 0:
                raise ValidationError("Quantity must be greater than zero")
