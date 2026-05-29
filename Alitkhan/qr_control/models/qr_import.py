from odoo import models, fields, api, _


class QrImport(models.Model):
    _name = 'qr.import'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Q&R Import'
    _rec_name = 'number'

    user_id = fields.Many2one('res.users', string="Salesman", required=True)
    number = fields.Char(string='Reference', readonly=True, copy=False, default=lambda self: _('New'))
    datetime = fields.Datetime(string="Created at", default=lambda self: fields.Datetime.now())
    qr_product_ids = fields.One2many('qr.product', 'import_id', string="Products")
    product_reservation_ids = fields.One2many('reserved.product', 'import_id', string="Reserved Records")
    reserved = fields.Boolean("Is All Reserved", default=False)
    company_id = fields.Many2one('res.company', 'Company', required=True, index=True,
                                 default=lambda self: self.env.company)

    @api.model
    def create(self, vals):
        if 'number' not in vals or vals['number'] == _('New'):
            vals['number'] = self.env['ir.sequence'].next_by_code('qr.import') or _('New')
        return super(QrImport, self).create(vals)

    def reserve_all(self):
        partners = self.qr_product_ids.mapped('required_partner_id')
        for partner in partners:
            rec_reserved_product = self.env['reserved.product'].search(
                []).filtered(
                lambda
                    pr: pr.import_id.id == self.id and pr.reserved_partner_id.id == partner.id
            )
            if not rec_reserved_product:
                rec_reserved_product = self.env['reserved.product'].create(
                    {
                        'import_id': self.id,
                        'reserved_partner_id': partner.id,
                    }
                )
            for qr_product in [x for x in self.qr_product_ids if x.qty_required > 0 and x.required_partner_id.id == partner.id]:
                reservation_line = self.env['reserved.product.line'].create(
                    {
                        'reserved_product_id': rec_reserved_product.id,
                        'product_id': qr_product.product_id.id,
                        'qty_reserved': qr_product.qty_required,
                        'qr_product_id': qr_product.id
                    })
                qr_product.virtual_reservation_line_id = reservation_line.id
        self.reserved = True

    def unreserve_all(self):
        if self.product_reservation_ids:
            self.product_reservation_ids.sudo().unlink()
        self.reserved = False

    def button_reservation_entries(self):
        return {
            'name': _('Reservation Entries'),
            'view_mode': 'list,form',
            'res_model': 'reserved.product',
            'view_id': False,
            'type': 'ir.actions.act_window',
            'domain': [('id', 'in', self.mapped('product_reservation_ids').ids)],
        }


class QrProduct(models.Model):
    _name = 'qr.product'
    _description = 'Q&R Product'
    _rec_name = 'default_code'

    import_id = fields.Many2one('qr.import', string="Import Rec")
    product_id = fields.Many2one('product.product', string="Product")
    default_code = fields.Char(string="Internal Reference", related='product_id.default_code')
    qty_available = fields.Float(string="Qty Onhand", store=True, readonly=True,
                                 related='product_id.qty_available')
    virtual_available = fields.Float(string="Forecast Quantity", store=True, readonly=True,
                                     related='product_id.virtual_available')
    free_available_qty = fields.Float(string="Available Quantity", store=True, readonly=True,
                                      related='product_id.free_available_qty')
    reserved_qty = fields.Float(string="Reserved Quantity", store=True, readonly=True,
                                related='product_id.reserved_qty')
    incoming_qty = fields.Float(string="Incoming Quantity", store=True, readonly=True,
                                related='product_id.incoming_qty')
    qty_required = fields.Float(string="Quantity Required", compute_sudo=False,
                                digits='Product Unit of Measure')
    required_partner_id = fields.Many2one('res.partner', string="Required for")
    reserved_operation_ids = fields.One2many('reserve.operation', 'qr_product_id',
                                             string="Reserved Operations", readonly=True)
    incoming_operation_ids = fields.One2many('incoming.operation', 'qr_product_id',
                                             string="Incoming Operations", readonly=True)
    picking_ids = fields.Many2many('stock.picking', 'picking_qr_product_rel', 'qr_product_id', 'pid',
                                   string="Pickings", store=True, readonly=True)
    production_ids = fields.Many2many('mrp.production', string="Manufacturing Orders", store=True, readonly=True)
    virtual_reservation_line_id = fields.Many2one('reserved.product.line', string="Reservation Line")
    company_id = fields.Many2one('res.company', 'Company', required=True, index=True,
                                 default=lambda self: self.env.company)
    in_picking_ids = fields.Many2many('stock.picking', 'in_picking_qr_product_rel', 'qr_product_id', 'pid',
                                      string="Incoming Pickings", store=True, readonly=True)
    out_picking_ids = fields.Many2many('stock.picking', 'out_picking_qr_product_rel', 'qr_product_id', 'pid',
                                       string="Outgoing Pickings", store=True, readonly=True)

    def reserve_product(self):
        product_reservation = self.env['reserved.product'].search(
            []).filtered(
            lambda pr: pr.import_id.id == self.import_id.id and pr.reserved_partner_id.id == self.required_partner_id.id
        )
        if not product_reservation:
            product_reservation = self.env['reserved.product'].create(
                {
                    'import_id': self.import_id.id,
                    'reserved_partner_id': self.required_partner_id.id,
                }
            )
        rec_reserved_product = self.env['reserved.product.line'].create(
            {
                'reserved_product_id': product_reservation.id,
                'product_id': self.product_id.id,
                'qty_reserved': self.qty_required,
                'qr_product_id': self.id
            }
        )
        self.virtual_reservation_line_id = rec_reserved_product

    def unreserve_product(self):
        self.virtual_reservation_line_id.sudo().unlink()
        product_reservation = self.env['reserved.product'].search(
            []).filtered(
            lambda pr: pr.import_id.id == self.import_id.id and pr.reserved_partner_id.id == self.required_partner_id.id
        )
        if not product_reservation.mapped('reserve_product_ids'):
            product_reservation.sudo().unlink()

    def create(self, vals):
        res = super(QrProduct, self).create(vals)
        for qr_product in [x for x in res]:
            pickings = self.env['stock.move.line'].sudo().search([]).filtered(
                lambda ml: ml.product_id.id == qr_product.product_id.id and ml.quantity_product_uom > 0
            ).mapped('picking_id')
            if pickings:
                for picking in pickings:
                    if picking.picking_type_id.code == "outgoing":
                        lines = self.env['stock.move.line'].sudo().search(
                            [('picking_id', '=', picking.id)]).filtered(
                            lambda ml: ml.product_id.id == qr_product.product_id.id and ml.quantity_product_uom > 0)
                        self.env['reserve.operation'].create({
                            'qr_product_id': qr_product.id,
                            'operation_type': "transfer",
                            'picking_id': picking.id,
                            'partner_id': picking.partner_id.id,
                            'user_id': picking.sale_id.user_id.id,
                            'qty_reserved': sum(lines.mapped('quantity_product_uom'))
                        })
                    if picking.picking_type_id.code == "incoming":
                        lines = self.env['stock.move.line'].sudo().search(
                            [('picking_id', '=', picking.id)]).filtered(
                            lambda ml: ml.product_id.id == qr_product.product_id.id and ml.quantity_product_uom > 0)
                        self.env['incoming.operation'].create({
                            'qr_product_id': qr_product.id,
                            'picking_id': picking.id,
                            'qty_reserved': sum(lines.mapped('quantity_product_uom'))
                        })
                qr_product.picking_ids = [picking.id for picking in pickings]
                qr_product.in_picking_ids = [picking.id for picking in pickings if picking.picking_type_id.code == "incoming"]
                qr_product.out_picking_ids = [picking.id for picking in pickings if picking.picking_type_id.code == "outgoing"]
            production_orders = self.env['mrp.production'].sudo().search([]).mapped('move_raw_ids').filtered(
                lambda m: m.product_id.id == qr_product.product_id.id and m.reserved_availability > 0
            ).mapped('raw_material_production_id')
            if production_orders:
                qr_product.production_ids = [production_order.id for production_order in production_orders]
                for production_order in production_orders:
                    moves = self.env['stock.move'].sudo().search(
                        [('raw_material_production_id', '=', production_order.id)]).filtered(
                        lambda m: m.product_id.id == qr_product.product_id.id and m.reserved_availability > 0)
                    self.env['reserve.operation'].create({
                        'qr_product_id': qr_product.id,
                        'operation_type': "mo",
                        'mo_id': production_order.id,
                        'user_id': production_order.user_id.id,
                        'qty_reserved': sum(moves.mapped('reserved_availability'))
                    })
        return res


class ReserveOperation(models.Model):
    _name = 'reserve.operation'
    _description = 'Reserved Operations'
    _rec_name = 'operation_type'

    qr_product_id = fields.Many2one('qr.product', string="Q&R Product")
    operation_type = fields.Selection([('transfer', 'Transfer'), ('mo', 'MO')])
    picking_id = fields.Many2one('stock.picking', string="Transfer", ondelete='cascade')
    mo_id = fields.Many2one('mrp.production', string="Manufacturing Order")
    user_id = fields.Many2one('res.users', string="Responsible")
    partner_id = fields.Many2one('res.partner', string="Contact")
    qty_reserved = fields.Float(string="Quantity Reserved", compute_sudo=False,
                                digits='Product Unit of Measure')
    company_id = fields.Many2one('res.company', 'Company', required=True, index=True,
                                 default=lambda self: self.env.company)


class IncomingOperation(models.Model):
    _name = 'incoming.operation'
    _description = 'Incoming Operations'
    _rec_name = 'name'

    qr_product_id = fields.Many2one('qr.product', string="Q&R Product")
    picking_id = fields.Many2one('stock.picking', string="Picking")
    name = fields.Char('Reference', related='picking_id.name')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('waiting', 'Waiting Another Operation'),
        ('confirmed', 'Waiting'),
        ('assigned', 'Ready'),
        ('done', 'Done'),
        ('cancel', 'Cancelled'),
    ], string='Status', related='picking_id.state')
    scheduled_date = fields.Datetime('Scheduled Date', related='picking_id.scheduled_date')
    location_id = fields.Many2one('stock.location', "Source Location", related='picking_id.location_id')
    location_dest_id = fields.Many2one('stock.location', "Destination Location", related='picking_id.location_dest_id')
    partner_id = fields.Many2one('res.partner', 'Contact', related='picking_id.partner_id')
    qty_reserved = fields.Float(string="Quantity", compute_sudo=False,
                                digits='Product Unit of Measure')
