# -*- coding: utf-8 -*-

import time

from odoo import api, fields, models, _
from odoo.exceptions import UserError


class CustomSaleAdvancePaymentInvoice(models.TransientModel):
    _inherit = 'sale.advance.payment.inv'

    def create_invoices(self):
        res = super(CustomSaleAdvancePaymentInvoice, self).create_invoices()
        self.env['sale.order'].browse(self._context.get('active_ids', [])).confirm_activity_ids.action_feedback(
            feedback="Invoice Created")
        return res
