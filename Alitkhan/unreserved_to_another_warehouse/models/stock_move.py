from werkzeug import urls

from odoo import api, fields, models, _
from odoo.http import request
from odoo.tools.float_utils import float_compare, float_is_zero, float_round
from odoo.exceptions import RedirectWarning, UserError, ValidationError


class ServerAction(models.Model):
    """ Add website option in server actions. """

    _inherit = 'ir.actions.server'

    def stock_unreserved_issue(self):
        StockQuant = self.env['stock.quant']
        StockMoveLine = self.env['stock.move.line']

        move_line_ids = []

        for quant in StockQuant.search([]):
            domain = [
                ('product_id', '=', quant.product_id.id),
                ('location_id', '=', quant.location_id.id),
                ('lot_id', '=', quant.lot_id.id),
                ('package_id', '=', quant.package_id.id),
                ('owner_id', '=', quant.owner_id.id),
                ('quantity', '!=', 0),
            ]
            move_lines = StockMoveLine.search(domain)
            move_line_ids += move_lines.ids

            reserved_on_move_lines = sum(move_lines.mapped('quantity'))

            if quant.location_id.should_bypass_reservation():
                if quant.reserved_quantity != 0:
                    quant.reserved_quantity = 0
            else:
                if quant.reserved_quantity <= 0:
                    if move_lines:
                        move_lines.with_context(
                            bypass_reservation_update=True).write({
                            'quantity_product_uom': 0
                        })
                    if quant.reserved_quantity < 0:
                        quant.reserved_quantity = 0
                elif reserved_on_move_lines != quant.reserved_quantity or any(
                        ml.quantity < 0 for ml in move_lines):
                    move_lines.with_context(
                        bypass_reservation_update=True).write({
                        'quantity_product_uom': 0
                    })
                    quant.reserved_quantity = 0

        # Unreserve move lines that are not associated with any quant
        remaining_move_lines = StockMoveLine.search([
            ('product_id.type', '=', 'consu'),
            ('quantity', '!=', 0),
            ('id', 'not in', move_line_ids),
        ])

        move_lines_to_unreserve = remaining_move_lines.filtered(
            lambda ml: not ml.location_id.should_bypass_reservation()
        ).ids

        if move_lines_to_unreserve:
            query = """
                UPDATE stock_move_line
                SET quantity_product_uom = 0, quantity = 0
                WHERE id = ANY(%s)
            """
            self.env.cr.execute(query, (move_lines_to_unreserve,))

    class StockQuant(models.Model):
        _inherit = 'stock.quant'

    #     @api.model
    #     def _update_reserved_quantity(self, product_id, location_id, quantity,
    #                                   lot_id=None, package_id=None,
    #                                   owner_id=None, strict=False):
    #         """ Increase the reserved quantity, i.e. increase `reserved_quantity` for the set of quants
    #         sharing the combination of `product_id, location_id` if `strict` is set to False or sharing
    #         the *exact same characteristics* otherwise. Typically, this method is called when reserving
    #         a move or updating a reserved move line. When reserving a chained move, the strict flag
    #         should be enabled (to reserve exactly what was brought). When the move is MTS,it could take
    #         anything from the stock, so we disable the flag. When editing a move line, we naturally
    #         enable the flag, to reflect the reservation according to the edition.
    #
    #         :return: a list of tuples (quant, quantity_reserved) showing on which quant the reservation
    #             was done and how much the system was able to reserve on it
    #         """
    #         self = self.sudo()
    #
    #         rounding = product_id.uom_id.rounding
    #         quants = self._gather(
    #             product_id, location_id, lot_id=lot_id,
    #             package_id=package_id, owner_id=owner_id, strict=strict
    #         )
    #         reserved_quants = []
    #
    #         # Determine action: reserve or unreserve
    #         is_reserve = float_compare(quantity, 0,
    #                                    precision_rounding=rounding) > 0
    #         is_unreserve = float_compare(quantity, 0,
    #                                      precision_rounding=rounding) < 0
    #
    #         # Validate availability
    #         if is_reserve:
    #             available_qty = sum(
    #                 quant.quantity - quant.reserved_quantity
    #                 for quant in quants
    #                 if float_compare(quant.quantity, 0,
    #                                  precision_rounding=rounding) > 0
    #             )
    #             if float_compare(quantity, available_qty,
    #                              precision_rounding=rounding) > 0:
    #                 raise UserError(_(
    #                     'It is not possible to reserve more products of %s than you have in stock.'
    #                 ) % product_id.display_name)
    #
    #         elif is_unreserve:
    #             reserved_total = sum(
    #                 quant.reserved_quantity for quant in quants)
    #             if float_compare(abs(quantity), reserved_total,
    #                              precision_rounding=rounding) > 0:
    #                 action_fix_unreserve = self.env.ref(
    #                     'stock.stock_quant_stock_move_line_desynchronization',
    #                     raise_if_not_found=False
    #                 )
    #                 if action_fix_unreserve and self.user_has_groups(
    #                         'base.group_system'):
    #                     raise RedirectWarning(
    #                         _("""It is not possible to unreserve more products of %s than you have in stock.
    # The correction could unreserve some operations with problematics products.""") % product_id.display_name,
    #                         action_fix_unreserve.id,
    #                         _('Automated action to fix it')
    #                     )
    #                 else:
    #                     self.env.ref(
    #                         'unreserved_to_another_warehouse.model_reserve_move_action_share'
    #                     ).create_action()
    #                     return []
    #
    #         else:
    #             return []
    #
    #         # Perform reservation/unreservation
    #         remaining_qty = quantity
    #         for quant in quants:
    #             if is_reserve:
    #                 free_qty = quant.quantity - quant.reserved_quantity
    #                 if float_compare(free_qty, 0,
    #                                  precision_rounding=rounding) <= 0:
    #                     continue
    #                 reserve_amount = min(free_qty, remaining_qty)
    #                 quant.reserved_quantity += reserve_amount
    #                 reserved_quants.append((quant, reserve_amount))
    #                 remaining_qty -= reserve_amount
    #
    #             elif is_unreserve:
    #                 unreserve_amount = min(quant.reserved_quantity,
    #                                        abs(remaining_qty))
    #                 quant.reserved_quantity -= unreserve_amount
    #                 reserved_quants.append((quant, -unreserve_amount))
    #                 remaining_qty += unreserve_amount
    #
    #             # Stop if no more quantity to reserve/unreserve
    #             if float_is_zero(remaining_qty, precision_rounding=rounding):
    #                 break
    #
    #         return reserved_quants
