# -*- coding: utf-8 -*-

from odoo import api, fields, models, _


class StockPicking(models.Model):
    _inherit = "stock.picking"

    virtual_reservation_id = fields.Many2one('reserved.product', related='sale_id.virtual_reservation_id',
                                             string="Virtual Reservation")
    qty_incoming = fields.Float('Quantity', digits='Product Unit of Measure')
    lot_ids = fields.Many2many('stock.lot', 'picking_lot_rel', 'picking_id', 'lot_id',
                               string="Lots/Serial")

    def button_validate(self):
        res = super().button_validate()
        for sp in self:
            if sp.virtual_reservation_id:
                for line in sp.virtual_reservation_id.reserve_product_ids:
                    line.qty_reserved = 0
                    line.qr_product_id.qty_required = 0
                sp.virtual_reservation_id.state = "done"
        return res

    def fields_view_get(self, view_id=None, view_type='list', toolbar=True,
                        submenu=True):
        res = super().fields_view_get(view_id=view_id, view_type=view_type,
                                      toolbar=toolbar, submenu=submenu)
        if self._context.get('qr_product_import'):
            if toolbar:
                res['toolbar']['print'] = []
                res['toolbar']['action'] = []
        return res


class StockQuant(models.Model):
    _inherit = 'stock.quant'

    free_qty = fields.Float('Available Qty', compute='_compute_free_qty')

    @api.depends('inventory_quantity', 'reserved_quantity')
    def _compute_free_qty(self):
        for quant in self:
            quant.free_qty = quant.inventory_quantity - quant.reserved_quantity

    @api.model
    def _get_free_quants_action(self, domain=None, extend=False):
        """ Returns an action to open quant view.
        Depending of the context (user have right to be inventory mode or not),
        the list view will be editable or readonly.

        :param domain: List for the domain, empty by default.
        :param extend: If True, enables form, graph and pivot views. False by default.
        """
        if not self.env['ir.config_parameter'].sudo().get_param('stock.skip_quant_tasks'):
            self._quant_tasks()
        ctx = dict(self.env.context or {})
        ctx.pop('group_by', None)
        ctx['search_default_internal_loc'] = True
        action = {
            'name': _('Available Quantity'),
            'view_type': 'list',
            'view_mode': 'list',
            'res_model': 'stock.quant',
            'type': 'ir.actions.act_window',
            'context': ctx,
            'domain': domain or [],
            'help': """
                        <p class="o_view_nocontent_empty_folder">No Stock On Hand</p>
                        <p>This analysis gives you an overview of the current stock
                        level of your products.</p>
                        """
        }

        target_action = self.env.ref('stock.dashboard_open_quants', False)
        if target_action:
            action['id'] = target_action.id

        action['view_id'] = self.env.ref('qr_control.view_stock_free_quant_tree').id
        # Enables form view in readonly list
        action.update({
            'view_mode': 'list,form',
            'views': [
                (action['view_id'], 'list'),
                (self.env.ref('stock.view_stock_quant_form').id, 'form'),
            ],
        })

        return action
