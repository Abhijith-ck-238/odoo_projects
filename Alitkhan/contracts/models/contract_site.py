# -*- coding: utf-8 -*-

from odoo import models, fields, api

class ContractSites(models.Model):
    _name = "contract.site"
    _rec_name = "site_name"

    site_name = fields.Char(string="Site Name")
    site_number = fields.Integer(string="Site Number")
    site_province = fields.Many2one("contract.province", string="province")
