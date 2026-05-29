# -*- coding: utf-8 -*-

# from odoo import models, fields, api


# class itkan_report_mod(models.Model):
#     _name = 'itkan_report_mod.itkan_report_mod'
#     _description = 'itkan_report_mod.itkan_report_mod'

#     name = fields.Char()
#     value = fields.Integer()
#     value2 = fields.Float(compute="_value_pc", store=True)
#     description = fields.Text()
#
#     @api.depends('value')
#     def _value_pc(self):
#         for record in self:
#             record.value2 = float(record.value) / 100
