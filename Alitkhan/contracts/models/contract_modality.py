# -*- coding: utf-8 -*-

from odoo import models, fields

class ContractModality(models.Model):
    _name = "contract.modality"
    _rec_name = "name"

    name = fields.Char(string="Name")
    user_ids = fields.Many2many("res.users", string="Managers")
