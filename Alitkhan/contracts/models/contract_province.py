# -*- coding: utf-8 -*-

from odoo import models, fields

class ContractProvince(models.Model):
    _name="contract.province"
    _rec_name="name"
    name=fields.Char(string="Governorate")
    prov_number = fields.Integer(string="Number")
    sites = fields.One2many('contract.site', 'site_province', readonly=True)
