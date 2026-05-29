from odoo import models
from odoo.tools.float_utils import float_compare


class CustomStockBackorderConfirmation(models.TransientModel):
    _inherit = 'stock.backorder.confirmation'
    _description = 'Backorder Confirmation'

    def _process(self, cancel_backorder=False):
        for confirmation in self:
            if cancel_backorder:
                for pick_id in confirmation.pick_ids:
                    moves_to_log = {}
                    for move in pick_id.move_lines:
                        if float_compare(move.product_uom_qty,
                                         move.quantity_done,
                                         precision_rounding=move.product_uom.rounding) > 0:
                            moves_to_log[move] = (move.quantity_done, move.product_uom_qty)
                    pick_id._log_less_quantities_than_expected(moves_to_log)
            for rec in confirmation.pick_ids:
                rec.x_studio_field_0PV4C = rec.origin
                confirmation.pick_ids.with_context(cancel_backorder=cancel_backorder).action_done()
            for pick in confirmation.pick_ids:
                sale_id = self.env['sale.order'].sudo().search([('name', '=', pick.origin)])
                picking_ids = self.env['stock.picking'].search([('origin', '=', pick.origin)])
                for pickid in picking_ids:
                    pickid.sale_id = sale_id
