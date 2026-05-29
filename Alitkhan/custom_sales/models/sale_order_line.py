from odoo import models, fields, _, api
from odoo.tools import float_compare
from odoo.exceptions import UserError
from markupsafe import Markup



class SaleOrderLineInherit(models.Model):
    _inherit = 'sale.order.line'

    config = fields.Many2one('offering.config', string="Config")
    is_exchange = fields.Boolean(string="Is Exchange", default=False,
                                 copy=False)
    vendor_id = fields.Many2one('res.partner', string="Vendor")
    vendor_price = fields.Float("Vendor Price")

    def _action_launch_stock_rule(self, previous_product_uom_qty=False):
        """
        Launch procurement group run method with required/custom fields genrated by a
        sale order line. procurement group will launch '_run_pull', '_run_buy' or '_run_manufacture'
        depending on the sale order line product rule.
        """
        precision = self.env['decimal.precision'].precision_get('Product Unit of Measure')
        procurements = []
        errors = []
        for line in self:
            if line.state != 'sale' or not line.product_id.type in ('consu', 'product'):
                continue
            qty = line._get_qty_procurement(previous_product_uom_qty)

            if float_compare(qty, line.product_uom_qty, precision_digits=precision) >= 0:
                continue

            group_id = line._get_procurement_group()
            if not group_id:
                group_id = self.env['procurement.group'].create(line._prepare_procurement_group_vals())
                line.order_id.procurement_group_id = group_id
            else:
                # In case the procurement group is already created and the order was
                # cancelled, we need to update certain values of the group.
                # if line.product_id.pack_ids:
                if line.sale_pack_id.product_lines:
                    values = line._prepare_procurement_values(group_id=line.order_id.procurement_group_id)
                    for val in values:

                        try:
                            pro_id = self.env['product.product'].browse(val.get('product_id'))
                            stock_id = self.env['stock.location'].browse(val.get('partner_dest_id'))
                            product_uom_obj = self.env['uom.uom'].browse(val.get('product_uom'))
                            procurements.append(self.env['procurement.group'].Procurement(
                                pro_id, 0, product_uom_obj,
                                line.order_id.partner_shipping_id.property_stock_customer,
                                val.get('name'), val.get('origin'), line.order_id.company_id, val
                            ))

                        except UserError as error:
                            errors.append(error.name)
                else:
                    updated_vals = {}
                    if group_id.partner_id != line.order_id.partner_shipping_id:
                        updated_vals.update({'partner_id': line.order_id.partner_shipping_id.id})
                    if group_id.move_type != line.order_id.picking_policy:
                        updated_vals.update({'move_type': line.order_id.picking_policy})
                    if updated_vals:
                        group_id.write(updated_vals)

            # if line.product_id.pack_ids:
            if line.sale_pack_id.product_lines:
                values = line._prepare_procurement_values(group_id=line.order_id.procurement_group_id)

                for val in values:

                    try:
                        pro_id = self.env['product.product'].browse(val.get('product_id'))
                        stock_id = self.env['stock.location'].browse(val.get('partner_dest_id'))
                        product_uom_obj = self.env['uom.uom'].browse(val.get('product_uom'))
                        procurements.append(self.env['procurement.group'].Procurement(
                            pro_id, val.get('product_qty'), product_uom_obj,
                            line.order_id.partner_shipping_id.property_stock_customer,
                            val.get('name'), val.get('origin'), line.order_id.company_id, val
                        ))

                    except UserError as error:
                        errors.append(error.name)
            else:
                values = line._prepare_procurement_values(group_id=group_id)
                product_qty = line.product_uom_qty - qty
                line_uom = line.product_uom
                quant_uom = line.product_id.uom_id
                product_qty, procurement_uom = line_uom._adjust_uom_quantities(product_qty, quant_uom)
                procurements.append(self.env['procurement.group'].Procurement(
                    line.product_id, product_qty, procurement_uom,
                    line.order_id.partner_shipping_id.property_stock_customer,
                    line.name, line.order_id.name, line.order_id.company_id, values))
        if procurements:
            self.env['procurement.group'].run(procurements)
            for picking_id in self.order_id.picking_ids:
                self.order_id.picking_ids = [(2, picking_id.id)]
            list_of_line_contents_of_stock = []

            location_dest_id = self.order_id.partner_id.property_stock_customer

            # product_category = self.env.ref("custom_sales_team.product_category_all_")
            # print("product_category",product_category)

            # Get source location
            location_id = self.order_id.warehouse_id.lot_stock_id.id

            for item in self.order_id.order_line:
                # if item.product_id.categ_id.id == product_category.id:
                #     raise UserError(
                #         _('Please set a category for the product %s.') % (
                #             item.product_id.name))
                # else:
                if item.config:
                    list_of_line_contents_of_stock.append((0, 0, {
                        "display_type": 'line_section',
                        "name": item.product_id.name,
                        "product_id": item.product_id.id,
                        "product_uom": item.product_uom.id,
                        "product_uom_qty": item.product_uom_qty,
                        "sale_line_id": item.id,
                        "location_id": location_id,
                        "location_dest_id": location_dest_id.id,
                    }))
                    for confglne in item.config.product_bom_lines:
                        list_of_line_contents_of_stock.append((0, 0, {
                            "product_id": confglne.product_id.id,
                            "name": confglne.product_id.name,
                            "product_uom_qty": item.product_uom_qty * confglne.qty,
                            "product_uom": confglne.uom_id.id if confglne.uom_id else item.product_uom.id,
                            "location_id": location_id,
                            "location_dest_id": location_dest_id.id,
                        }))

                else:
                    if not item.display_type and item.product_id and item.product_id.type in ('consu', 'product'):
                        list_of_line_contents_of_stock.append((0, 0, {
                            "product_id": item.product_id.id,
                            "name": item.product_id.name,
                            "product_uom_qty": item.product_uom_qty,
                            "product_uom": item.product_uom.id,
                            "sale_line_id": item.id,
                            "location_id": location_id,
                            "location_dest_id": location_dest_id.id,
                        }))

            stock_picking_vals = {"partner_id": self.order_id.partner_id.id,
                                  "state": "assigned",
                                  'origin': self.order_id.name,
                                  "location_id": location_id,
                                  "location_dest_id": location_dest_id.id,
                                  "move_ids_without_package": list_of_line_contents_of_stock,
                                  "picking_type_id": self.order_id.warehouse_id.out_type_id.id,
                                  "sale_id": self.order_id.id,
                                  "move_type": 'direct',
                                  }
            picking_id = self.env["stock.picking"].create(stock_picking_vals)
            picking_id.message_post(
                body=Markup(
                    'This transfer has been created from : <a href=# data-oe-model=sale.order data-oe-id=%d>%s</a>') % (
                         self.order_id.id, self.order_id.name))
            picking_id.action_confirm()

            picking_id.write({
                'state': 'assigned',
            })
            self.order_id.picking_ids = [(4, picking_id.id, None)]
            if self.order_id.env.user.has_group('sale.group_auto_done_setting'):
                self.order_id.action_confirm()
            if self.order_id.has_exchange_product:
                note = _("Scheduled activity to Handle exchanged items: %s") % (
                    self.order_id.name)
                self.order_id.activity_schedule(
                    'custom_sales.mail_activity_sale_order',
                    note=note,
                    user_id=self.order_id.user.id)

        module = self.env['ir.module.module'].sudo().search(
            [('state', '=', 'installed'), ('name', '=', 'procurement_jit')], limit=1)
        if module:
            orders = list(set(x.order_id for x in self))
            for order in orders:
                reassign = order.picking_ids.filtered(
                    lambda x: x.state == 'confirmed' or (x.state in ['waiting', 'assigned'] and not x.printed))
                if reassign:
                    reassign.action_assign()
        return True

    # def _action_launch_stock_rule(self, previous_product_uom_qty=False):
    #     """
    #     Launch procurement group run method with required/custom fields genrated by a
    #     sale order line. procurement group will launch '_run_pull', '_run_buy' or '_run_manufacture'
    #     depending on the sale order line product rule.
    #     """
    #     precision = self.env['decimal.precision'].precision_get('Product Unit of Measure')
    #     procurements = []
    #     errors = []
    #     for line in self:
    #         if line.state != 'sale' or not line.product_id.type in ('consu', 'product'):
    #             continue
    #         qty = line._get_qty_procurement(previous_product_uom_qty)
    #
    #         if float_compare(qty, line.product_uom_qty, precision_digits=precision) >= 0:
    #             continue
    #
    #         group_id = line._get_procurement_group()
    #         if not group_id:
    #             group_id = self.env['procurement.group'].create(line._prepare_procurement_group_vals())
    #             line.order_id.procurement_group_id = group_id
    #         else:
    #             # In case the procurement group is already created and the order was
    #             # cancelled, we need to update certain values of the group.
    #             # if line.product_id.pack_ids:
    #             if line.sale_pack_id.product_lines:
    #                 values = line._prepare_procurement_values(group_id=line.order_id.procurement_group_id)
    #                 for val in values:
    #
    #                     try:
    #                         pro_id = self.env['product.product'].browse(val.get('product_id'))
    #                         stock_id = self.env['stock.location'].browse(val.get('partner_dest_id'))
    #                         product_uom_obj = self.env['uom.uom'].browse(val.get('product_uom'))
    #                         procurements.append(self.env['procurement.group'].Procurement(
    #                             pro_id, 0, product_uom_obj,
    #                             line.order_id.partner_shipping_id.property_stock_customer,
    #                             val.get('name'), val.get('origin'), line.order_id.company_id, val
    #                         ))
    #
    #                     except UserError as error:
    #                         errors.append(error.name)
    #             else:
    #                 updated_vals = {}
    #                 if group_id.partner_id != line.order_id.partner_shipping_id:
    #                     updated_vals.update({'partner_id': line.order_id.partner_shipping_id.id})
    #                 if group_id.move_type != line.order_id.picking_policy:
    #                     updated_vals.update({'move_type': line.order_id.picking_policy})
    #                 if updated_vals:
    #                     group_id.write(updated_vals)
    #
    #         # if line.product_id.pack_ids:
    #         if line.sale_pack_id.product_lines:
    #             values = line._prepare_procurement_values(group_id=line.order_id.procurement_group_id)
    #
    #             for val in values:
    #
    #                 try:
    #                     pro_id = self.env['product.product'].browse(val.get('product_id'))
    #                     stock_id = self.env['stock.location'].browse(val.get('partner_dest_id'))
    #                     product_uom_obj = self.env['uom.uom'].browse(val.get('product_uom'))
    #                     procurements.append(self.env['procurement.group'].Procurement(
    #                         pro_id, val.get('product_qty'), product_uom_obj,
    #                         line.order_id.partner_shipping_id.property_stock_customer,
    #                         val.get('name'), val.get('origin'), line.order_id.company_id, val
    #                     ))
    #
    #                 except UserError as error:
    #                     errors.append(error.name)
    #         else:
    #             values = line._prepare_procurement_values(group_id=group_id)
    #             product_qty = line.product_uom_qty - qty
    #             line_uom = line.product_uom
    #             quant_uom = line.product_id.uom_id
    #             product_qty, procurement_uom = line_uom._adjust_uom_quantities(product_qty, quant_uom)
    #             procurements.append(self.env['procurement.group'].Procurement(
    #                 line.product_id, product_qty, procurement_uom,
    #                 line.order_id.partner_shipping_id.property_stock_customer,
    #                 line.name, line.order_id.name, line.order_id.company_id, values))
    #     if procurements:
    #         self.env['procurement.group'].run(procurements)
    #         for picking_id in self.order_id.picking_ids:
    #             self.order_id.picking_ids = [(2, picking_id.id)]
    #         list_of_line_contents_of_stock = []
    #
    #         location_dest_id = self.order_id.partner_id.property_stock_customer
    #
    #         # product_category = self.env.ref("custom_sales_team.product_category_all_")
    #         # print("product_category",product_category)
    #
    #         # Get source location
    #         location_id = self.order_id.warehouse_id.lot_stock_id.id
    #
    #         for item in self.order_id.order_line:
    #             # if item.product_id.categ_id.id == product_category.id:
    #             #     raise UserError(
    #             #         _('Please set a category for the product %s.') % (
    #             #             item.product_id.name))
    #             # else:
    #             if item.config:
    #                 list_of_line_contents_of_stock.append((0, 0, {
    #                     "display_type": 'line_section',
    #                     "name": item.product_id.name,
    #                     "product_id": item.product_id.id,
    #                     "product_uom": item.product_uom.id,
    #                     "product_uom_qty": item.product_uom_qty,
    #                     "sale_line_id": item.id,
    #                     "location_id": location_id,
    #                     "location_dest_id": location_dest_id.id,
    #                 }))
    #                 for confglne in item.config.product_bom_lines:
    #                     list_of_line_contents_of_stock.append((0, 0, {
    #                         "product_id": confglne.product_id.id,
    #                         "name": confglne.product_id.name,
    #                         "product_uom_qty": item.product_uom_qty * confglne.qty,
    #                         "product_uom": confglne.uom_id.id if confglne.uom_id else item.product_uom.id,
    #                         "location_id": location_id,
    #                         "location_dest_id": location_dest_id.id,
    #                     }))
    #
    #             else:
    #                 if not item.display_type:
    #                     list_of_line_contents_of_stock.append((0, 0, {
    #                         "product_id": item.product_id.id,
    #                         "name": item.product_id.name,
    #                         "product_uom_qty": item.product_uom_qty,
    #                         "product_uom": item.product_uom.id,
    #                         "sale_line_id": item.id,
    #                         "location_id": location_id,
    #                         "location_dest_id": location_dest_id.id,
    #                     }))
    #
    #         stock_picking_vals = {"partner_id": self.order_id.partner_id.id,
    #                               "state": "assigned",
    #                               'origin': self.order_id.name,
    #                               "location_id": location_id,
    #                               "location_dest_id": location_dest_id.id,
    #                               "move_ids_without_package": list_of_line_contents_of_stock,
    #                               "picking_type_id": self.order_id.warehouse_id.out_type_id.id,
    #                               "sale_id": self.order_id.id,
    #                               "move_type": 'direct',
    #                               }
    #         picking_id = self.env["stock.picking"].create(stock_picking_vals)
    #         picking_id.message_post(
    #             body=Markup(
    #                 'This transfer has been created from : <a href=# data-oe-model=sale.order data-oe-id=%d>%s</a>') % (
    #                      self.order_id.id, self.order_id.name))
    #         picking_id.action_confirm()
    #
    #         picking_id.write({
    #             'state': 'assigned',
    #         })
    #         self.order_id.picking_ids = [(4, picking_id.id, None)]
    #         if self.order_id.env.user.has_group('sale.group_auto_done_setting'):
    #             self.order_id.action_confirm()
    #         if self.order_id.has_exchange_product:
    #             note = _("Scheduled activity to Handle exchanged items: %s") % (
    #                 self.order_id.name)
    #             self.order_id.activity_schedule(
    #                 'custom_sales.mail_activity_sale_order',
    #                 note=note,
    #                 user_id=self.order_id.user.id)
    #
    #     module = self.env['ir.module.module'].sudo().search(
    #         [('state', '=', 'installed'), ('name', '=', 'procurement_jit')], limit=1)
    #     if module:
    #         orders = list(set(x.order_id for x in self))
    #         for order in orders:
    #             reassign = order.picking_ids.filtered(
    #                 lambda x: x.state == 'confirmed' or (x.state in ['waiting', 'assigned'] and not x.printed))
    #             if reassign:
    #                 reassign.action_assign()
    #     return True