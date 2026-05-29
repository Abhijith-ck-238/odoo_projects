# -*- coding: utf-8 -*-

from odoo import models, fields, api

class ContractCondition(models.Model):
    _name="contract.condition"
    _rec_name="name"

    name=fields.Char(string="Condition")
