# -*- coding: utf-8 -*-
###############################################################################
#
#    Cybrosys Technologies Pvt. Ltd.
#
#    Copyright (C) 2026-TODAY Cybrosys Technologies(<https://www.cybrosys.com>)
#    Author: Abhijith CK (odoo@cybrosys.com)
#
#    This program is under the terms of the Odoo Proprietary License v1.0(OPL-1)
#    It is forbidden to publish, distribute, sublicense, or sell copies of the
#    Software or modified copies of the Software.
#
#    THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#    IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#    FITNESS FOR A PARTICULAR PURPOSE AND NON INFRINGEMENT.
#    IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM,
#    DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR
#    OTHERWISE,ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE
#    USE OR OTHER DEALINGS IN THE SOFTWARE.
#
###############################################################################
from datetime import date, timedelta
from odoo import api, fields, models, _


class ProductToRfq(models.TransientModel):
    """ Wizard for adding products in rfq """
    _name = 'product.to.rfq'
    _description = "Product To RFQ"
    _rec_name = "product_id"

    product_id = fields.Many2one('product.product', string="Product",
                                 readonly=True, help="Product Name")
    qty = fields.Float(string="Quantity", default=1.00, help="Product Quantity")
    order_id = fields.Many2one('purchase.order', string="RFQ No.",
                               readonly=True, help="Purchase Order")
    price_unit = fields.Float(string="Unit Price",
                              help="Price unit of the product")
    recent_products_ids = fields.One2many('recent.products.tree.purchase',
                                          'purchase_id',
                                          string="Recent Products",
                                          help="Recent products purchased")
    recent_date = fields.Datetime(string="Recent Purchase From",
                                  default=lambda self: fields.Datetime.now() - timedelta(days=30),
                                  help="Recent date")

    @api.onchange('recent_date')
    def _onchange_recent_date(self):
        """ Returns the recent purchase details of the product """
        purchase_order_ids = self.env['purchase.order.line'].search(
            [('product_id', '=', self.product_id.id),
             ('order_id.date_order', '>=', self.recent_date),
             ('state', '=', 'purchase'),
             ])
        vals = purchase_order_ids.mapped(lambda record: (0, 0, {
            'order_line_id': record.id,
        }))
        self.recent_products_ids = vals

    def action_add_to_rfq(self):
        """Add products to RFQ from wizard"""
        self.ensure_one()

        order = self.order_id
        product = self.product_id

        # Prepare display name
        name = product.display_name
        if product.description_sale:
            name += '\n' + product.description_sale

        # Find existing line with same product & price
        order_line = order.order_line.filtered(
            lambda l: l.product_id == product and l.price_unit == self.price_unit
        )

        if order_line:
            order_line.product_qty += self.qty
        else:
            self.env['purchase.order.line'].create({
                'order_id': order.id,
                'product_id': product.id,
                'name': name,
                'product_qty': self.qty,
                'price_unit': self.price_unit,
                'product_uom': product.product_tmpl_id.uom_id.id,
                'date_planned': fields.Datetime.now(),
            })

        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'type': 'success',
                'message': _('Product successfully added to %s') % order.name,
                'next': {'type': 'ir.actions.act_window_close'},
            }
        }
