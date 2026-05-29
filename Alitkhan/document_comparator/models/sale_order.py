# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError


class SaleOrderCompInh(models.Model):
    _inherit = "sale.order"

    compare_docs = fields.One2many("document.comparator", 'sale_order')

    def open_compare_form(self, context={}):
        form_view_id = self.env.ref(
            "document_comparator.document_comparator_form").id
        tree_view_id = self.env.ref(
            "document_comparator.document_comparator_tree").id

        context.update({"default_document_type": "sale_order",
                        "default_sale_order": self.id})

        return {
            'type': 'ir.actions.act_window',
            'name': 'Compared Document',
            'view_type': 'form',
            'view_mode': 'list',
            'res_model': 'document.comparator',
            'views': [(tree_view_id, 'list'), (form_view_id, 'form')],
            'domain': [('sale_order', '=', self.id)],
            'target': 'current',
            'context': context,
            # 'target':'new' makes it purchase_orderp up

        }
