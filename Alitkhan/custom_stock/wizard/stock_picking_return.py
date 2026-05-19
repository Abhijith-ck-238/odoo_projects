from odoo import models, fields, api, _
from odoo.tools.float_utils import float_round
from odoo.exceptions import UserError


class StockReturnPickingLine(models.TransientModel):
    _inherit = "stock.return.picking.line"

    lot_id = fields.Many2one(
        'stock.lot',
        string="Lot/Serial Number",
    )


class ReturnPicking(models.TransientModel):
    _inherit = 'stock.return.picking'

    move_dest_exists = fields.Boolean(string='Move Destination Exists',
                                      default=False)
    parent_location_id = fields.Many2one('stock.location',
                                         string='Parent Location')
    original_location_id = fields.Many2one('stock.location',
                                           string='Original Location')
    location_id = fields.Many2one(
        'stock.location', 'Return Location')

    @api.onchange('picking_id')
    def _onchange_picking_id(self):
        move_dest_exists = False
        product_return_moves = [(5,)]
        if self.picking_id and self.picking_id.state != 'done':
            raise UserError(_("You may only return Done pickings."))
        for move in self.picking_id.move_ids_without_package:
            if move.state == 'cancel':
                continue
            if move.scrapped:
                continue
            if move.move_dest_ids:
                move_dest_exists = True
            for move_line in move.move_line_ids:
                product_return_moves.append((0, 0,
                                             self._prepare_stock_return_picking_line_vals_from_move(
                                                 move, move_line)))
        if self.picking_id and not product_return_moves:
            raise UserError(
                _("No products to return (only lines in Done state and not fully returned yet can be returned)."))
        if self.picking_id:
            self.product_return_moves = product_return_moves
            self.move_dest_exists = move_dest_exists
            self.parent_location_id = self.picking_id.picking_type_id.warehouse_id and self.picking_id.picking_type_id.warehouse_id.view_location_id.id or self.picking_id.location_id.location_id.id
            self.original_location_id = self.picking_id.location_id.id
            location_id = self.picking_id.location_id.id
            if self.picking_id.picking_type_id.return_picking_type_id.default_location_dest_id.return_location:
                location_id = self.picking_id.picking_type_id.return_picking_type_id.default_location_dest_id.id
            self.location_id = location_id

    @api.model
    def _prepare_stock_return_picking_line_vals_from_move(self, stock_move, move_line):
        quantity = stock_move.quantity - sum(
            stock_move.move_dest_ids
            .filtered(lambda m: m.state in ['partially_available', 'assigned',
                                            'done'])
            .mapped('move_line_ids.quantity')
        )
        quantity = float_round(quantity,
                               precision_rounding=stock_move.product_uom.rounding)
        return {
            'product_id': stock_move.product_id.id,
            'lot_id': move_line.lot_id.id,
            'move_id': stock_move.id,
            'uom_id': stock_move.product_id.uom_id.id,
        }

    def _prepare_move_default_values(self, return_line, new_picking):
        vals = {
            'product_id': return_line.product_id.id,
            'product_uom_qty': return_line.quantity,
            'product_uom': return_line.product_id.uom_id.id,
            'picking_id': new_picking.id,
            'state': 'draft',
            'date_expected': fields.Datetime.now(),
            'location_id': return_line.move_id.location_dest_id.id,
            'location_dest_id': self.location_id.id or return_line.move_id.location_id.id,
            'picking_type_id': new_picking.picking_type_id.id,
            'warehouse_id': self.picking_id.picking_type_id.warehouse_id.id,
            'origin_returned_move_id': return_line.move_id.id,
            'procure_method': 'make_to_stock',
            # 'lot_id': return_line.lot_id.id
            # 'move_line_ids': [
            #     (0,0,{
            #         'lot_id': return_line.lot_id.id,
            #         'product_uom_id': return_line.product_id.uom_id.id,
            #         'location_id': return_line.move_id.location_dest_id.id,
            #         'location_dest_id': self.location_id.id or return_line.move_id.location_id.id,
            #         'product_id': return_line.product_id.id
            #     })
            # ]
        }
        return vals

    def _create_returns(self):
        for return_move in self.product_return_moves.mapped('move_id'):
            return_move.move_dest_ids.filtered(lambda m: m.state not in ('done', 'cancel'))._do_unreserve()

        # create new picking for returned products
        picking_type_id = self.picking_id.picking_type_id.return_picking_type_id.id or self.picking_id.picking_type_id.id
        new_picking = self.picking_id.copy({
            'move_ids_without_package': [],
            'picking_type_id': picking_type_id,
            'state': 'draft',
            'origin': _("Return of %s") % self.picking_id.name,
            'location_id': self.picking_id.location_dest_id.id,
            'location_dest_id': self.location_id.id})



        new_picking.message_post_with_view('mail.message_origin_link',
            values={'self': new_picking, 'origin': self.picking_id},
            subtype_id=self.env.ref('mail.mt_note').id)
        returned_lines = 0
        for return_line in self.product_return_moves:
            if not return_line.move_id:
                raise UserError(_("You have manually created product lines, please delete them to proceed."))
            # TODO sle: float_is_zero?
            if return_line.quantity:
                returned_lines += 1
                vals = self._prepare_move_default_values(return_line, new_picking)
                r = return_line.move_id.copy(vals)
                vals = {}

                # +--------------------------------------------------------------------------------------------------------+
                # |       picking_pick     <--Move Orig--    picking_pack     --Move Dest-->   picking_ship
                # |              | returned_move_ids              ↑                                  | returned_move_ids
                # |              ↓                                | return_line.move_id              ↓
                # |       return pick(Add as dest)          return toLink                    return ship(Add as orig)
                # +--------------------------------------------------------------------------------------------------------+
                move_orig_to_link = return_line.move_id.move_dest_ids.mapped('returned_move_ids')
                move_dest_to_link = return_line.move_id.move_orig_ids.mapped('returned_move_ids')
                vals['move_orig_ids'] = [(4, m.id) for m in move_orig_to_link | return_line.move_id]
                vals['move_dest_ids'] = [(4, m.id) for m in move_dest_to_link]
                r.write(vals)
                r.write({
                    'move_line_ids': [
                        (0,0,{
                            'lot_id': return_line.lot_id.id,
                            'product_uom_id': return_line.product_id.uom_id.id,
                            'location_id': return_line.move_id.location_dest_id.id,
                            'location_dest_id': self.location_id.id or return_line.move_id.location_id.id,
                            'product_id': return_line.product_id.id,
                            'picking_id':new_picking.id
                        })
                    ]
                })
        if not returned_lines:
            raise UserError(_("Please specify at least one non-zero quantity."))
        new_picking.action_confirm()
        new_picking.action_assign()
        new_picking = self.env['stock.picking'].browse([new_picking.id])
        # new_picking = self.env['stock.picking'].browse([new_picking.id])
        for move in new_picking.move_ids_without_package:
            return_picking_line = self.product_return_moves.filtered(lambda r: r.move_id == move.origin_returned_move_id)
            for return_line in return_picking_line:
                if return_line and return_line.to_refund:
                    move.to_refund = True
        return new_picking.id, picking_type_id
