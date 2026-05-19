# -*- coding: utf-8 -*-

from odoo import models, fields, api


class ItkanResPartnerArName(models.Model):

    _inherit = "res.partner"
    # _rec_name = "display_name"

    arabic_name = fields.Char(string="Arabic Name")
    display_name = fields.Char()
    full_name = fields.Char(compute="_compute_display_name")

    @api.constrains("name", "arabic_name")
    def compute_mixed_name(self):
        for item in self:
            if item.arabic_name and item.name:
                item.display_name = item.arabic_name + " - " + item.name
                item.full_name = item.arabic_name + " - " + item.name
            else:
                item.display_name = item.name
                item.full_name = item.name

    @api.depends("name", "arabic_name")
    def _compute_display_name(self):
        for item in self:
            if item.arabic_name and item.name:
                item.display_name = item.arabic_name + " - " + item.name
                item.full_name = item.arabic_name + " - " + item.name
            else:
                item.display_name = item.name or ""
                item.display_name = item.name or ""





class ItkanPayRollExtExt(models.Model):
    _inherit="hr.employee"

    arabic_name = fields.Char(string="Arabic name")
