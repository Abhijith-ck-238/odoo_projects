from odoo import api, fields, models,_
from odoo.exceptions import UserError


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    bill_total = fields.Float('Billed Total', compute="_compute_bill_amount")
    paid_amount = fields.Float('Paid Amount', compute="_compute_paid_amount")
    remaining = fields.Float('Remaining', compute="_compute_remaining")
    open_order = fields.Float('Open Order', compute='_compute_open_order')
    analytic_precision = fields.Integer(
        store=False,
        default=lambda self: self.env['decimal.precision'].precision_get("Percentage Analytic"),
    )
    analytic_distribution = fields.Json(
        'Analytic Distribution',
        store=True,
        copy=True,
        readonly=False,
    )

    def action_save_analytic_distribution(self):
        for rec in self:
            if not rec.analytic_distribution:
                raise UserError(_("Please add analytic distribution lines before saving."))

            # Update all order lines with the analytic distribution
            rec.order_line.write({
                'analytic_distribution': rec.analytic_distribution
            })

        return True

    @api.depends('invoice_ids')
    def _compute_bill_amount(self):
        for rec in self:
            rec.bill_total = sum(rec.invoice_ids.filtered(lambda r: r.state != 'cancel').mapped('amount_total'))


    @api.depends('invoice_ids')
    def _compute_paid_amount(self):
        for rec in self:
            amount_due = sum(rec.invoice_ids.filtered(lambda r: r.state != 'cancel').mapped('amount_residual'))
            amount_billed = sum(rec.invoice_ids.filtered(lambda r: r.state != 'cancel').mapped('amount_total'))
            rec.paid_amount = amount_billed - amount_due

    @api.depends('amount_total', 'bill_total')
    def _compute_open_order(self):
        for rec in self:
            rec.open_order = rec.amount_total - rec.bill_total


    @api.depends('bill_total', 'paid_amount')
    def _compute_remaining(self):
        for rec in self:
            rec.remaining = rec.bill_total - rec.paid_amount


    @api.model
    def _default_warehouse_id(self):
        company = self.env.company.id
        warehouse_ids = self.env['stock.warehouse'].search(
            [('company_id', '=', company)], limit=1)
        return warehouse_ids

    @api.model
    def _default_picking_type(self):
        return self._get_picking_type(
            self.env.context.get('company_id') or self.env.company.id)

    READONLY_STATES = {
        'purchase': [('readonly', True)],
        'done': [('readonly', True)],
        'cancel': [('readonly', True)],
    }

    @api.model
    def _get_default_purchase_team(self):
        return self.env['purchase.team']._get_default_team_id()

    team_id = fields.Many2one(
        'purchase.team', string='Purchase Team',
        default=_get_default_purchase_team,
        domain="['|', ('company_id', '=', False), "
               "('company_id', '=', company_id)]")
    warehouse_id = fields.Many2one(
        'stock.warehouse', string='Warehouse',
        required=True, readonly=True,
        states={'draft': [('readonly', False)], 'sent': [('readonly', False)]},
        default=_default_warehouse_id, check_company=True)
    picking_type_id = fields.Many2one('stock.picking.type', 'Deliver To',
                                      states=READONLY_STATES,
                                      required=True,
                                      default=_default_picking_type,
                                      domain="['|', ('warehouse_id', '=', False), ('warehouse_id.company_id', '=', company_id)]",
                                      help="This will determine operation type of incoming shipment")

    @api.model
    def _get_picking_type(self, company_id):
        team = self._get_default_purchase_team()
        warehouse_id = team.warehouse_id
        picking_type = self.env['stock.picking.type'].search(
            [('code', '=', 'incoming'),
             ('warehouse_id.company_id', '=', company_id),
             ('warehouse_id', '=', warehouse_id.id)])
        if not picking_type:
            picking_type = self.env['stock.picking.type'].search(
                [('code', '=', 'incoming'),
                 ('warehouse_id', '=', warehouse_id.id)])
        return picking_type[:1]

    @api.onchange('team_id')
    def _onchange_team_id(self):
        self.warehouse_id = self.team_id.warehouse_id
        company_id = self.env.context.get('company_id') or self.env.company.id

        picking_type = self.env['stock.picking.type'].search(
            [('code', '=', 'incoming'),
             ('warehouse_id.company_id', '=', company_id),
             ('warehouse_id', '=', self.warehouse_id.id)])
        self.picking_type_id = picking_type.id

    def button_confirm(self):
        res = super().button_confirm()

        for order in self:
            for picking in order.picking_ids.filtered(
                    lambda p: p.picking_type_code == 'incoming'):
                for move in picking.move_ids_without_package:
                    # Custom logic: find a suitable internal location
                    stock_quant = self.env['stock.quant'].search([
                        ('product_id', '=', move.product_id.id),
                        ('quantity', '>', 0),
                        ('location_id.usage', '=', 'internal')
                    ], order='id DESC', limit=1)
                    if stock_quant:
                        move.location_dest_id = stock_quant.location_id.id  # updates move
                        for line in move.move_line_ids:
                            line.location_dest_id = stock_quant.location_id.id  # updates move lines too
        return res
