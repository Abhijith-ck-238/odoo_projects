# -*- coding: utf-8 -*-

from odoo import models, fields, api


class SaleOrderLineExt(models.Model):
    _inherit="sale.order"

    print_lot = fields.Boolean(string="Print lot no.")
    print_exp = fields.Boolean(string="Print lot exp")
    print_note = fields.Boolean(string="Print lot note")
    add_temp_footer = fields.Boolean(string="Add temp footer")