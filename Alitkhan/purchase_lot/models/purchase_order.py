# -*- coding: utf-8 -*-

from odoo import api, fields, models, api, _
from odoo.exceptions import ValidationError


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    create_lot = fields.Boolean(string="Can create Lot", default=True)

    def button_confirm(self):
        res = super(PurchaseOrder, self).button_confirm()
        for line in [x for x in self.order_line if x.stock_production_lot_ids]:
            lot_ids = line.stock_production_lot_ids.mapped('id')
            index = 0
            for move_line in line.move_ids.move_line_ids:
                move_line.write({
                    'lot_id': lot_ids[index],
                    'quantity': line.stock_production_lot_ids.filtered(
                        lambda l: l.id == lot_ids[index]
                    ).po_line_lot_id.product_qty
                })
                index += 1
            del lot_ids[:index]
            for lot_id in lot_ids:
                self.env['stock.move.line'].create({
                    'move_id': line.move_ids.move_line_ids[0].move_id.id,
                    'product_id': line.product_id.id,
                    'product_uom_id': line.product_id.uom_id.id,
                    'picking_id': line.move_ids.move_line_ids[0].picking_id.id,
                    'location_id': line.move_ids.move_line_ids[0].location_id.id,
                    'location_dest_id': line.move_ids.move_line_ids[0].location_dest_id.id,
                    'lot_id': lot_id,
                    'quantity': line.stock_production_lot_ids.filtered(
                        lambda l: l.id == lot_id
                    ).po_line_lot_id.product_qty
                })
        return res

    def action_create_lot(self):
        purchase_lots = self.order_line.mapped('purchase_product_lot_ids')
        if not purchase_lots:
            raise ValidationError(_('No Purchase Lot found!'))
        for lot in purchase_lots:
            stock_production_lot = self.env['stock.lot'].create(
                {
                    'name': lot.name,
                    'ref': lot.ref,
                    'product_id': lot.product_id.id,
                    'product_qty': lot.product_qty,
                    'company_id': lot.company_id.id,
                    'po_line_id': lot.po_line_id.id,
                    'po_line_lot_id': lot.id,
                    'use_date': lot.use_date,
                    'alert_date': lot.alert_date
                }
            )
            lot.lot_id = stock_production_lot.id
        self.create_lot = False


class PurchaseOrderLine(models.Model):
    _inherit = "purchase.order.line"

    purchase_product_lot_ids = fields.One2many('purchase.product.lot', 'po_line_id')
    stock_production_lot_ids = fields.One2many('stock.lot', 'po_line_id')
    display_assign_lots = fields.Boolean(compute='_compute_display_assign_lots')

    @api.depends('product_id', 'product_id.tracking')
    def _compute_display_assign_lots(self):
        for line in self:
            line.display_assign_lots = False
            if line.product_id:
                line.display_assign_lots = (
                        line.product_id.tracking == 'lot'
                )

    def write(self, vals):
        result = super(PurchaseOrderLine, self).write(vals)
        if 'purchase_product_lot_ids' in vals:
            for line in self:
                if line.product_qty < sum(line.purchase_product_lot_ids.mapped('product_qty')):
                    raise ValidationError(_('Total Lot quantity should not be greater than Quantity.'))
                if line.product_qty != sum(line.purchase_product_lot_ids.mapped('product_qty')):
                    raise ValidationError(_('Please provide Lot for the whole Quantities.'))
        return result

    def button_lot_entries(self):
        return {
            'name': _('Lot/Serial Entries'),
            'view_mode': 'tree,form',
            'res_model': 'stock.lot',
            'view_id': False,
            'type': 'ir.actions.act_window',
            'domain': [('id', 'in', self.mapped('stock_production_lot_ids').ids)],
        }

    def action_open_purchase_lot(self):
        view = self.env.ref('purchase_lot.view_purchase_line_lot')
        return {
            'name': _('Lot/Serial Numbers'),
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'purchase.order.line',
            'views': [(view.id, 'form')],
            'view_id': view.id,
            'target': 'new',
            'res_id': self.id,
        }


class ProductionLot(models.Model):
    _inherit = 'stock.lot'

    po_line_id = fields.Many2one('purchase.order.line')
    po_line_lot_id = fields.Many2one('purchase.product.lot', string="Purchase Line Lot/Serial")
