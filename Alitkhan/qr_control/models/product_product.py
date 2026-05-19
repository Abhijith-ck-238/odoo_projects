from odoo import models, fields, api, _
from odoo.addons.stock.models.product import OPERATORS
from odoo.osv import expression
from odoo.exceptions import UserError


class ProductProduct(models.Model):
    _inherit = 'product.product'

    reserved_qty = fields.Float(
        'Reserved Quantity', compute='_compute_available_reserved_quantities',
        compute_sudo=False, digits='Product Unit of Measure')
    free_available_qty = fields.Float(
        'Available Quantity', compute='_compute_available_reserved_quantities',
        compute_sudo=False, digits='Product Unit of Measure')
    qr_reserved_product_ids = fields.One2many('reserved.product.line',
                                              'product_id',
                                              string="Reserved Records")
    virtual_reserved_qty = fields.Float(
        'Virtual Reserved Quantity',
        compute='_compute_virtual_reserved_quantities',
        search='_search_virtual_reserved_quantities',
        compute_sudo=False, digits='Product Unit of Measure')
    stock_move_line_ids = fields.One2many('stock.move.line', 'product_id',
                                          string="Move Lines")

    on_hand_locations = fields.Char(compute='compute_on_hand_locations',
                                    store=False,
                                    inverse="_inverse_on_hand_locations")

    @api.depends('stock_quant_ids')
    def compute_on_hand_locations(self):
        for rec in self:
            location_domain = rec._get_domain_locations()[0]
            domain = expression.AND(
                [[('product_id', 'in', rec.ids)], location_domain])
            ctx = dict(self.env.context)
            ctx.update({'no_at_date': True})
            stock_quant_ids = self.env['stock.quant'].with_context(ctx).search(
                domain)
            if not stock_quant_ids:
                rec.on_hand_locations = False
            else:
                locations_with_quant = []
                for quant in stock_quant_ids:
                    location_name = quant.location_id.display_name + " : " + str(
                        quant.quantity)
                    locations_with_quant.append(location_name)
                on_hand_qty_with_loc = ','.join(
                    [p for p in locations_with_quant])
                rec.on_hand_locations = on_hand_qty_with_loc

    def _inverse_on_hand_locations(self):
        for rec in self:
            rec.on_hand_locations = rec.on_hand_locations

    def fields_view_get(self, view_id=None, view_type='form', toolbar=True,
                        submenu=True):
        res = super().fields_view_get(view_id=view_id, view_type=view_type,
                                      toolbar=toolbar, submenu=submenu)
        if self._context.get('search_default_filter_virtual_reserved_qty') == 1:
            if toolbar:
                res['toolbar']['print'] = []
                res['toolbar']['action'] = []
        return res

    @api.depends_context('company_owned', 'force_company', 'location',
                         'warehouse')
    def _compute_available_reserved_quantities(self):
        products = self.filtered(lambda p: p.type != 'service')
        for product in products:
            print(product.stock_move_line_ids,'abddddd',products)
            lines = product.stock_move_line_ids.filtered(
                lambda
                        ml: ml.quantity_product_uom > 0 and ml.picking_id.picking_type_id.code == "outgoing"
            )
            print(lines.read(),'abdddddd lineee')
            qty_reserved = sum(lines.mapped('quantity_product_uom'))
            production_orders = self.env['mrp.production'].sudo().search(
                []).mapped('move_raw_ids').filtered(
                lambda
                    m: m.product_id.id == product.id and m.quantity > 0
            ).mapped('raw_material_production_id')
            for production_order in production_orders:
                moves = self.env['stock.move'].sudo().search(
                    [('raw_material_production_id', '=',
                      production_order.id)]).filtered(
                    lambda
                        m: m.product_id.id == product.id and m.quantity > 0)
                qty_reserved = qty_reserved + sum(
                    moves.mapped('quantity'))
            product.reserved_qty = qty_reserved
            product.free_available_qty = product.qty_available - qty_reserved
        services = self - products
        services.free_available_qty = services.reserved_qty = 0.0

    @api.depends_context('qr_reserved_product_ids')
    def _compute_virtual_reserved_quantities(self):
        products = self.filtered(lambda p: p.type != 'service')
        for product in products:
            res_lines = self.env['reserved.product.line'].sudo().search(
                []).sudo().filtered(lambda l: l.product_id.id == product.id)
            product.virtual_reserved_qty = sum(res_lines.mapped('qty_reserved'))
            # product.virtual_reserved_qty = sum(product.sudo().qr_reserved_product_ids.sudo().mapped('qty_reserved'))
        services = self - products
        services.virtual_reserved_qty = 0.0

    def _search_virtual_reserved_quantities(self, operator, value):
        if operator not in OPERATORS:
            raise UserError(_("Invalid domain operator %s") % operator)
        if not isinstance(value, (float, int)):
            raise UserError(_("Invalid domain right operand %s") % value)

        ids = []
        for product in self.search([]):
            if OPERATORS[operator](product.virtual_reserved_qty, value):
                ids.append(product.id)
        return [("id", "in", ids)]

    def action_product_virtual_reservation_report(self):
        return {
            'name': _('Reservation Lines'),
            'view_mode': 'list,form',
            'res_model': 'reserved.product.line',
            'view_id': False,
            'type': 'ir.actions.act_window',
            'domain': [
                ('id', 'in', self.mapped('qr_reserved_product_ids').ids)],
        }

    def action_open_reserved(self):
        pickings = self.stock_move_line_ids.filtered(
            lambda ml: ml.quantity_product_uom > 0
        ).mapped('picking_id')
        for picking in pickings:
            if picking.picking_type_code == "outgoing":
                move_lines = self.env['stock.move.line'].sudo().search(
                    [('picking_id', '=', picking.id)]).filtered(
                    lambda
                        ml: ml.product_id.id == self.id and ml.quantity_product_uom > 0)
                qty = sum(move_lines.mapped('quantity_product_uom'))
                lots = move_lines.mapped('lot_id')
                picking.write({
                    'qty_incoming': qty,
                    'lot_ids': [(6, 0, [y for y in lots.ids])]
                })
        ctx = self._context.copy()
        ctx['qr_product_import'] = True
        return {
            'name': _('Pickings'),
            'view_mode': 'list',
            'res_model': 'stock.picking',
            'view_id': self.env.ref(
                'qr_control.view_incoming_pickings_tree').id,
            'type': 'ir.actions.act_window',
            'domain': [('id', 'in', [picking.id for picking in pickings if
                                     picking.picking_type_code == "outgoing"])],
            'context': ctx
        }

    def action_open_incoming(self):
        pickings = self.stock_move_line_ids.filtered(
            lambda ml: ml.quantity_product_uom > 0
        ).mapped('picking_id')
        for picking in pickings:
            if picking.picking_type_code == "incoming":
                move_lines = self.env['stock.move.line'].sudo().search(
                    [('picking_id', '=', picking.id)]).filtered(
                    lambda
                        ml: ml.product_id.id == self.id and ml.quantity_product_uom > 0)
                lots = move_lines.mapped('lot_id')
                qty = sum(move_lines.mapped('quantity_product_uom'))
                picking.write({
                    'qty_incoming': qty,
                    'lot_ids': [(6, 0, [y for y in lots.ids])]
                })
        ctx = self._context.copy()
        ctx['qr_product_import'] = True
        return {
            'name': _('Pickings'),
            'view_mode': 'list',
            'res_model': 'stock.picking',
            'view_id': self.env.ref(
                'qr_control.view_incoming_pickings_tree').id,
            'type': 'ir.actions.act_window',
            'domain': [('id', 'in', [picking.id for picking in pickings if
                                     picking.picking_type_code == "incoming"])],
            'context': ctx,
        }

    def action_open_free_quants(self):
        domain = [('product_id', 'in', self.ids)]
        hide_location = not self.env.user.has_group(
            'stock.group_stock_multi_locations')
        hide_lot = all([product.tracking == 'none' for product in self])
        self = self.with_context(hide_location=hide_location, hide_lot=hide_lot)

        # If user have rights to write on quant, we define the view as editable.
        if self.env.user.has_group('stock.group_stock_manager'):
            self = self.with_context(inventory_mode=True)
            # Set default location id if multilocations is inactive
            if not self.env.user.has_group('stock.group_stock_multi_locations'):
                user_company = self.env.company
                warehouse = self.env['stock.warehouse'].search(
                    [('company_id', '=', user_company.id)], limit=1
                )
                if warehouse:
                    self = self.with_context(
                        default_location_id=warehouse.lot_stock_id.id)
        # Set default product id if quants concern only one product
        if len(self) == 1:
            self = self.with_context(
                default_product_id=self.id,
                single_product=True
            )
        else:
            self = self.with_context(product_tmpl_ids=self.product_tmpl_id.ids)
        ctx = dict(self.env.context)
        ctx.update({'no_at_date': True, 'search_default_on_hand': True})
        return self.env['stock.quant'].with_context(
            ctx)._get_free_quants_action(domain)


class ProductReservation(models.Model):
    _name = 'reserved.product'
    _description = 'Q&R Product Reservation'
    _rec_name = 'name'

    name = fields.Char(string='Reference', readonly=True, copy=False,
                       default=lambda self: _('New'))
    date = fields.Datetime(string="Created at",
                           default=lambda self: fields.Datetime.now())
    import_id = fields.Many2one('qr.import', string="Q&R Import")
    reserved_partner_id = fields.Many2one('res.partner', string="Reserved for")
    sale_id = fields.Many2one('sale.order', "Sale Order")
    reserve_product_ids = fields.One2many('reserved.product.line',
                                          'reserved_product_id',
                                          string="Product Reservation Lines")
    user_id = fields.Many2one('res.users', string="Salesman",
                              related='import_id.user_id',
                              store=True)
    state = fields.Selection([('draft', "Draft"), ("done", "Confirmed")],
                             string="State", default='draft', readonly=True)
    company_id = fields.Many2one('res.company', 'Company', required=True,
                                 index=True,
                                 default=lambda self: self.env.company)

    def unlink(self):
        children = self.mapped('reserve_product_ids')
        if children:
            children.unlink()
        return super(ProductReservation, self).unlink()

    def action_create_so(self):
        order_lines = []
        for reservation_line in self.reserve_product_ids:
            vals_list = {}
            vals_list.update(
                product_id=reservation_line.product_id.id,
                product_uom_qty=reservation_line.qty_reserved
            )
            order_lines.append((0, 0, vals_list))
        sale_order = self.env['sale.order'].sudo().create({
            'partner_id': self.reserved_partner_id.id,
            'virtual_reservation_id': self.id,
            'order_line': order_lines
        })
        self.sale_id = sale_order.id

    @api.model
    def create(self, vals):
        if 'name' not in vals or vals['name'] == _('New'):
            vals['name'] = self.env['ir.sequence'].next_by_code(
                'reserved.product') or _('New')
        return super(ProductReservation, self).create(vals)


class ProductReservationLine(models.Model):
    _name = 'reserved.product.line'
    _description = 'Q&R Product Reservation Line'
    _rec_name = 'product_id'

    reserved_product_id = fields.Many2one('reserved.product',
                                          string="Virtual Reservation")
    product_id = fields.Many2one('product.product', string="Product")
    qty_reserved = fields.Float('Reserved Quantity',
                                digits='Product Unit of Measure')
    qr_product_id = fields.Many2one('qr.product', string="QR Product")
    company_id = fields.Many2one('res.company', 'Company', required=True,
                                 index=True,
                                 default=lambda self: self.env.company)
    reserved_partner_id = fields.Many2one('res.partner', string="Reserved for",
                                          related='reserved_product_id.reserved_partner_id')
    user_id = fields.Many2one('res.users', string="Salesman",
                              related='reserved_product_id.user_id', store=True)
