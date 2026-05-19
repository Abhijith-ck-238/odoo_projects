from odoo import models, fields,_
# from odoo.tools.profiler import profile
from odoo.exceptions import UserError
from odoo.tools.float_utils import float_compare, float_round, float_is_zero
from itertools import groupby
from odoo.addons.sale_stock.models.stock import StockPicking


class StockMoveInherit(models.Model):
    _inherit = 'stock.move'

    sequence = fields.Integer(string='Sequence', default=10)
    display_type = fields.Selection([
        ('line_section', "Section"),
        ('line_note', "Note"),
        ],
        default=False,
        help="Technical field for UX purpose.")

    def _split(self, qty, restrict_partner_id=False):
        """ Splits `self` quantity and return values for a new moves to be created afterwards

        :param qty: float. quantity to split (given in product UoM)
        :param restrict_partner_id: optional partner that can be given in order to force the new move to restrict its choice of quants to the ones belonging to this partner.
        :returns: list of dict. stock move values """
        self.ensure_one()
        if self.state in ('done', 'cancel'):
            raise UserError(_('You cannot split a stock move that has been set to \'Done\' or \'Cancel\'.'))
        elif self.state == 'draft':
            # we restrict the split of a draft move because if not confirmed yet, it may be replaced by several other moves in
            # case of phantom bom (with mrp module). And we don't want to deal with this complexity by copying the product that will explode.
            raise UserError(_('You cannot split a draft move. It needs to be confirmed first.'))

        if float_is_zero(qty, precision_rounding=self.product_id.uom_id.rounding):
            return []

        decimal_precision = self.env['decimal.precision'].precision_get('Product Unit of Measure')

        # `qty` passed as argument is the quantity to backorder and is always expressed in the
        # quants UOM. If we're able to convert back and forth this quantity in the move's and the
        # quants UOM, the backordered move can keep the UOM of the move. Else, we'll create is in
        # the UOM of the quants.
        uom_qty = self.product_id.uom_id._compute_quantity(qty, self.product_uom, rounding_method='HALF-UP')
        if float_compare(qty,
                         self.product_uom._compute_quantity(uom_qty, self.product_id.uom_id, rounding_method='HALF-UP'),
                         precision_digits=decimal_precision) == 0:
            defaults = self._prepare_move_split_vals(uom_qty)
        else:
            defaults = self.with_context(force_split_uom_id=self.product_id.uom_id.id)._prepare_move_split_vals(qty)

        if restrict_partner_id:
            defaults['restrict_partner_id'] = restrict_partner_id

        # TDE CLEANME: remove context key + add as parameter
        if self.env.context.get('source_location_id'):
            defaults['location_id'] = self.env.context['source_location_id']
        new_move_vals = self.sudo().copy_data(defaults)

        # Update the original `product_qty` of the move. Use the general product's decimal
        # precision and not the move's UOM to handle case where the `quantity_done` is not
        # compatible with the move's UOM.
        new_product_qty = self.product_id.uom_id._compute_quantity(max(0, self.product_qty - qty), self.product_uom,
                                                                   round=False)
        new_product_qty = float_round(new_product_qty, precision_digits=self.env['decimal.precision'].precision_get(
            'Product Unit of Measure'))
        self.with_context(do_not_unreserve=True).write({'product_uom_qty': new_product_qty})
        return new_move_vals

    def _get_price_unit(self):
        """ Returns the unit price for the move"""
        self.ensure_one()
        if self.purchase_line_id and self.product_id.id == self.purchase_line_id.product_id.id:
            line = self.purchase_line_id
            order = line.order_id
            price_unit = line.price_unit
            if line.taxes_id:
                price_unit = line.taxes_id.with_context(round=False).compute_all(price_unit, currency=line.order_id.currency_id, quantity=1.0)['total_void']
            if line.product_uom.id != line.product_id.uom_id.id:
                price_unit *= line.product_uom.factor / line.product_id.uom_id.factor
            if order.sudo().currency_id != order.company_id.currency_id:
                price_unit = order.currency_id._convert(
                    price_unit, order.company_id.currency_id, order.company_id, fields.Date.context_today(self), round=False)
            # return price_unit
            return {self.env['stock.lot']: price_unit}
        return super(StockMoveInherit, self)._get_price_unit()



class StockMoveLineInherit(models.Model):
    _inherit = 'stock.move.line'
    name = fields.Text(string='Description', required=True)
    sequence = fields.Integer(string='Sequence', default=10)
    display_type = fields.Selection([
        ('line_section', "Section"),
        ('line_note', "Note"),
    ],
        default=False,
        help="Technical field for UX purpose.")


class ExtendStockPicking(models.Model):
    _inherit = 'stock.picking'
    _description = 'Stock Picking'

    x_studio_field_0PV4C = fields.Char(string="SO")
    site_id = fields.Many2one("contract.site", String="Site", related="sale_id.site_id")
    province = fields.Many2one("contract.province", string='Province', related="sale_id.province")
    sn_number = fields.Char(string="SN Number", related="sale_id.sn_number")

    def _needs_automatic_assign(self):
        self.ensure_one()
        if self.sale_id:
            return False
        return True

    
    # TODO : Commented Because sale_id is already fetching.
    # def _create_backorder_picking(self):
    #     self.ensure_one()
    #     return self.copy({
    #         'name': '/',
    #         'move_ids': [],
    #         'move_line_ids': [],
    #         'backorder_id': self.id,
    #         'sale_id':self.sale_id.id
    #     })
    #
    # def _create_backorder(self,backorder_moves=None):
    #
    #     """ This method is called when the user chose to create a backorder. It will create a new
    #     picking, the backorder, and move the stock.moves that are not `done` or `cancel` into it.
    #     """
    #     backorders = self.env['stock.picking']
    #     bo_to_assign = self.env['stock.picking']
    #     for picking in self:
    #         if backorder_moves:
    #             moves_to_backorder = backorder_moves.filtered(lambda m: m.picking_id == picking)
    #         else:
    #             moves_to_backorder = picking._get_moves_to_backorder()
    #         moves_to_backorder._recompute_state()
    #         if moves_to_backorder:
    #             backorder_picking = picking._create_backorder_picking()
    #             sale_idd = backorder_picking.sale_id
    #             moves_to_backorder.write({'picking_id': backorder_picking.id, 'picked': False})
    #             moves_to_backorder.move_line_ids.package_level_id.write({'picking_id': backorder_picking.id})
    #             moves_to_backorder.mapped('move_line_ids').write({'picking_id': backorder_picking.id})
    #             backorders |= backorder_picking
    #             backorder_picking.user_id = False
    #             picking.message_post(
    #                 body=_('The backorder %s has been created.', backorder_picking._get_html_link())
    #             )
    #             if backorder_picking.picking_type_id.reservation_method == 'at_confirm':
    #                 bo_to_assign |= backorder_picking
    #     if bo_to_assign:
    #         bo_to_assign.action_assign()
    #         bo_to_assign.sale_id = sale_idd.id
    #     return backorders
    #     # backorders = self.env['stock.picking']
    #     # for picking in self:
    #     #     moves_to_backorder = picking.move_line_ids.filtered(lambda x: x.state not in ('done', 'cancel'))
    #     #     if moves_to_backorder:
    #     #         backorder_picking = picking.copy({
    #     #             'name': '/',
    #     #             'move_lines': [],
    #     #             'move_line_ids': [],
    #     #             'backorder_id': picking.id,
    #     #             'sale_id': picking.sale_id.id
    #     #         })
    #     #         sale_idd = backorder_picking.sale_id
    #     #         picking.message_post(
    #     #             body=_('The backorder <a href=# data-oe-model=stock.picking data-oe-id=%d>%s</a> has been created.') % (
    #     #                 backorder_picking.id, backorder_picking.name))
    #     #         moves_to_backorder.write({'picking_id': backorder_picking.id})
    #     #         moves_to_backorder.move_line_ids.package_level_id.write({'picking_id': backorder_picking.id})
    #     #         moves_to_backorder.mapped('move_line_ids').write({'picking_id': backorder_picking.id})
    #     #         if backorder_picking._needs_automatic_assign():
    #     #             backorder_picking.action_assign()
    #     #             backorder_picking.sale_id = sale_idd.id
    #     #         backorders |= backorder_picking
    #     # return backorders

    def _log_activity_get_documents(self, orig_obj_changes, stream_field, stream, groupby_method=False):
        """ Generic method to log activity. To use with
        _log_activity method. It either log on uppermost
        ongoing documents or following documents. This method
        find all the documents and responsible for which a note
        has to be log. It also generate a rendering_context in
        order to render a specific note by documents containing
        only the information relative to the document it. For example
        we don't want to notify a picking on move that it doesn't
        contain.

        :param orig_obj_changes dict: contain a record as key and the
        change on this record as value.
        eg: {'move_id': (new product_uom_qty, old product_uom_qty)}
        :param stream_field string: It has to be a field of the
        records that are register in the key of 'orig_obj_changes'
        eg: 'move_dest_ids' if we use move as record (previous example)
            - 'UP' if we want to log on the upper most ongoing
            documents.
            - 'DOWN' if we want to log on following documents.
        :param groupby_method: Only need when
        stream is 'DOWN', it should group by tuple(object on
        which the activity is log, the responsible for this object)
        """
        if self.env.context.get('skip_activity'):
            return {}
        move_to_orig_object_rel = {co: ooc for ooc in orig_obj_changes.keys() for co in ooc[stream_field]}
        origin_objects = self.env[list(orig_obj_changes.keys())[0]._name].concat(*list(orig_obj_changes.keys()))
        # The purpose here is to group each destination object by
        # (document to log, responsible) no matter the stream direction.
        # example:
        # {'(delivery_picking_1, admin)': stock.move(1, 2)
        #  '(delivery_picking_2, admin)': stock.move(3)}
        visited_documents = {}
        if stream == 'DOWN':
            if groupby_method:
                grouped_moves = groupby(origin_objects.sudo().mapped(stream_field), key=groupby_method)
            else:
                raise AssertionError('You have to define a groupby method and pass them as arguments.')
        elif stream == 'UP':
            # When using upstream document it is required to define
            # _get_upstream_documents_and_responsibles on
            # destination objects in order to ascend documents.
            grouped_moves = {}
            for visited_move in origin_objects.mapped(stream_field):
                for document, responsible, visited in visited_move._get_upstream_documents_and_responsibles(
                        self.env[visited_move._name]):
                    if grouped_moves.get((document, responsible)):
                        grouped_moves[(document, responsible)] |= visited_move
                        visited_documents[(document, responsible)] |= visited
                    else:
                        grouped_moves[(document, responsible)] = visited_move
                        visited_documents[(document, responsible)] = visited
            grouped_moves = grouped_moves.items()
        else:
            raise AssertionError('Unknown stream.')

        documents = {}
        for (parent, responsible), moves in grouped_moves:
            if not parent:
                continue
            moves = self.env[moves[0]._name].concat(*moves)
            # Get the note
            rendering_context = {move: (orig_object, orig_obj_changes[orig_object]) for move in moves for orig_object in
                                 move_to_orig_object_rel[move]}
            if visited_documents:
                documents[(parent, responsible)] = rendering_context, visited_documents.values()
            else:
                documents[(parent, responsible)] = rendering_context
        return documents

def _action_done(self):
        res = super(StockPicking,self)._action_done()
        sale_order_lines_vals = []
        for move in self.move_ids:
            sale_order = move.picking_id.sale_id
            # Creates new SO line only when pickings linked to a sale order and
            # for moves with qty. done and not already linked to a SO line.
            if not sale_order or move.sale_line_id or not move.picked or not (
                (move.location_dest_id.usage in ['customer', 'transit'] and not move.move_dest_ids)
                or (move.location_id.usage == 'customer' and move.to_refund)
            ):
                continue
            product = move.product_id
            quantity = move.quantity
            if move.to_refund:
                quantity *= -1

            so_line_vals = {
                'move_ids': [(4, move.id, 0)],
                'name': product.display_name,
                'order_id': sale_order.id,
                'product_id': product.id,
                'product_uom_qty': 0,
                'qty_delivered': quantity,
                'product_uom': move.product_uom.id,
            }
            so_line = sale_order.order_line.filtered(lambda sol: sol.product_id == product)
            if product.invoice_policy == 'delivery':
                # Check if there is already a SO line for this product to get
                # back its unit price (in case it was manually updated).
                if so_line:
                    so_line_vals['price_unit'] = so_line[0].price_unit
            elif product.invoice_policy == 'order':
                # No unit price if the product is invoiced on the ordered qty.
                so_line_vals['price_unit'] = 0
            # New lines should be added at the bottom of the SO (higher sequence number)
            if not so_line:
                so_line_vals['sequence'] = max(sale_order.order_line.mapped('sequence')) + len(sale_order_lines_vals) + 1
            sale_order_lines_vals.append(so_line_vals)

        if sale_order_lines_vals:
            lines_with_product_uom_qty = [line for line in sale_order_lines_vals if line.get('product_uom_qty', 0) != 0]
            self.env['sale.order.line'].with_context(skip_procurement=True).create(lines_with_product_uom_qty)
        return res
StockPicking._action_done = _action_done
