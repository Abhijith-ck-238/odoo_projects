# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError
import pandas as pd
import numpy as np


class DocumentCompRec(models.Model):
    _name = "document.comparator"

    name = fields.Char(readonly=True)
    description = fields.Char()
    document_type = fields.Selection(
        [("sale_order", "Sale Order"), ("purchase_order", "Purchase Order")],
        readonly=True)
    sale_order = fields.Many2one("sale.order", string="Sale Order",
                                 readonly=True)
    purchase_order = fields.Many2one("purchase.order", string="Purchase Order",
                                     readonly=True)
    state = fields.Selection(
        [('draft', 'Draft'), ('match', 'Match'), ('mismatch', 'Mismatch')],
        default='draft', readonly=True)
    order_line = fields.One2many("document.comparator.line", "compare_id",
                                 string="Order Lines")
    missing_order_line = fields.One2many("document.comparator.line",
                                         "missing_compare_id",
                                         string="Missing Products")
    include_prices = fields.Boolean(compute="_get_prices")

    @api.constrains("id", "document_type")
    def _compute_name(self):
        for item in self:
            if item.sale_order:
                sale_order_index = len(item.sale_order.compare_docs)
                item.name = item.sale_order.name + "-COMP-" + str(
                    sale_order_index).zfill(3)
            elif item.purchase_order:
                sale_order_index = len(item.purchase_order.compare_docs)
                item.name = item.purchase_order.name + "COMP-" + str(
                    sale_order_index).zfill(3)
            else:
                item.name = "NAN-COMP-" + str(item.id).zfill(3)

    def unlink(self):
        if self.state != 'draft':
            raise UserError(_("You can not delete a compared sheet"))
        else:
            res = super(DocumentCompRec, self).unlink()
            return res

    @api.depends("order_line")
    def _get_prices(self):
        for doc in self:
            if doc.order_line and sum(doc.order_line.mapped('price_unit')) > 0:
                doc.include_prices = True
            else:
                doc.include_prices = False

    def compare_items(self):
        doc_index = self.order_line.mapped('product_id.id')
        doc_qty = self.order_line.mapped("qty")
        doc_line_ids = self.order_line.mapped("id")
        doc_sheet = pd.DataFrame({
            'doc_id': doc_line_ids,
            'doc_qty': doc_qty,
            'in_doc': True,
        },
            index=doc_index)

        if self.include_prices:
            doc_prices = self.order_line.mapped("price_unit")
            doc_sheet['doc_price'] = doc_prices
        else:
            doc_sheet['doc_price'] = 0

        # For missing products
        missing_values = [(5, 0, 0)]
        if self.document_type == "sale_order" and self.sale_order:
            record = self.sale_order

        elif self.document_type == "purchase_order" and self.purchase_order:
            record = self.purchase_order

        else:
            raise UserError(
                _("Please Select a document type and sale/purcahse order to compare to"))

        record_index = record.order_line.mapped('product_id.id')
        record_qty = record.order_line.mapped("product_uom_qty")
        record_prices = record.order_line.mapped("price_unit")
        record_sheet = pd.DataFrame({
            'record_qty': record_qty,
            'in_record': True,
        },
            index=record_index)

        if self.include_prices:
            record_sheet['record_prices'] = record_prices
        else:
            record_sheet['record_prices'] = 0

        full_sheet = pd.concat([doc_sheet, record_sheet], axis=1)
        full_sheet['match'] = False
        full_sheet['qty_diff'] = full_sheet['doc_qty'].fillna(0) - full_sheet[
            'record_qty'].fillna(0)
        full_sheet['price_diff'] = full_sheet['doc_price'].fillna(0) - \
                                   full_sheet['record_prices'].fillna(0)

        full_sheet.loc[full_sheet['in_record'] & full_sheet['in_doc'] & \
                       (full_sheet['qty_diff'] == 0) & \
                       (full_sheet['price_diff'] == 0), 'match'] = True

        full_sheet = full_sheet.fillna(False)
        if full_sheet['match'].all():
            self.state = 'match'
        else:
            self.state = 'mismatch'

        for product_id, row in full_sheet.iterrows():
            if row.in_doc == True:

                line_id = self.env['document.comparator.line'].browse(
                    [row.doc_id])
                if row.match == True:
                    line_id.state = 'match'
                else:
                    line_id.state = 'unmatch' if row.in_record else 'unregistered'
                    line_id.qty_diff = row.qty_diff
                    line_id.price_diff = row.price_diff

            else:
                product_id = self.env['product.product'].browse([product_id])
                missing_values.append((0, 0, {
                    'product_id': product_id.id,
                    'part_number': product_id.default_code,
                    'qty_diff': -row.qty_diff,
                    'price_diff': -row.qty_diff,
                    'state': 'unregistered'
                }))

        if missing_values:
            self.write({'missing_order_line': missing_values})
        else:
            pass


class DocumentCompLine(models.Model):
    _name = "document.comparator.line"
    _order = "product_id"

    state = fields.Selection(
        [('match', 'Identical'), ('unmatch', 'Unidentical'),
         ('unregistered', 'Unregistered')])  # Add By Saeb
    compare_id = fields.Many2one('document.comparator')
    missing_compare_id = fields.Many2one('document.comparator')
    product_id = fields.Many2one("product.product", string="Product")
    product_smn = fields.Char(string="SMN")
    product_name = fields.Char(string="Product Name")
    part_number = fields.Char(string="Part Number")
    qty = fields.Float(string="Quantity")
    qty_diff = fields.Float(string="Quantity Difference", readonly=True)
    price_unit = fields.Float(string="Unit Price")
    price_diff = fields.Float(string="Unit Price Difference", readonly=True)

    @api.model
    def create(self, values):
        if values.get("product_smn"):
            smn = values["product_smn"]
            product_id = self.env['product.product'].search(
                [('default_code', 'like', smn)])
            if len(product_id) > 1:
                raise UserError(
                    _(f"More Than One Product Of The SMN {smn} Was Found. Please Contact Support"))
            elif len(product_id) == 1:
                values['product_id'] = product_id.id
            else:
                raise UserError(_(f"A Product with SMN {smn} was not  found"))
        else:
            pass

        result = super(DocumentCompLine, self).create(values)
        return result

    @api.constrains("part_number")
    def _handle_products(self):
        not_in_system = []
        for rec in self:
            product_obj = self.env["product.product"].search(
                ['&', ("default_code", "=", rec.part_number),
                 ("default_code", "!=", False)])
            if not product_obj:
                not_in_system.append(rec.product_name)
            if not_in_system:
                raise UserError(
                    _("The following Products are not in the system or has no Internal Reference %s") % str(
                        not_in_system))
            rec.product_id = product_obj.id
