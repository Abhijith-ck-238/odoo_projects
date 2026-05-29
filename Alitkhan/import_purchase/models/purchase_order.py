# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.
from odoo import models, fields, exceptions, api, _

class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    custom_seq = fields.Boolean('Custom Sequence')
    system_seq = fields.Boolean('System Sequence')
    purchase_name = fields.Char('Purchase Name')