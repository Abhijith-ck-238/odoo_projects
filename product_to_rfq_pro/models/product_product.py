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
from odoo import fields, models, _
from odoo.exceptions import UserError


class Product(models.Model):
    """ Inheriting 'product.product' to add products directly to RFQ """
    _inherit = 'product.product'

    def action_add_to_rfq_direct(self):
        """Add products directly to RFQ"""
        self.ensure_one()

        order = self.env['purchase.order'].browse(self._context.get('active_id'))
        if not order:
            raise UserError(_("No active purchase order in context."))

        # Prepare line name
        name = self.product_tmpl_id.display_name
        if self.product_tmpl_id.description_sale:
            name += '\n' + self.product_tmpl_id.description_sale

        price = self.product_tmpl_id.standard_price

        # Find existing order line with same product and price
        order_line = order.order_line.filtered(
            lambda l: l.product_id == self and l.price_unit == price
        )[:1]

        if order_line:
            order_line.product_qty += 1
        else:
            self.env['purchase.order.line'].create({
                'order_id': order.id,
                'product_id': self.id,
                'name': name,
                'product_qty': 1.0,
                'product_uom': self.product_tmpl_id.uom_id.id,
                'price_unit': price,
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

    def action_get_purchase_wizard(self):
        """We can get the wizard view"""
        res = {
            'name': _('Product Details'),
            'view_mode': 'form',
            'res_model': 'product.to.rfq',
            'type': 'ir.actions.act_window',
            'target': 'new',
            'context': {
                'default_order_id': self.env['purchase.order'].
                browse(self._context.get('active_id')).id,
                'default_product_id': self.id,
                'default_price_unit': self.product_tmpl_id.standard_price
            }
        }
        return res
