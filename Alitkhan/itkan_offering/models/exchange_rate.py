# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError
import datetime

class OfferingExchangeRate(models.Model):
    _name="offering.exchangerate"
    _rec_name="currency_name"

    currency_name = fields.Char(string="Currency Name")
    exchange_rate = fields.Float(string="Exchange Rate", default=1)