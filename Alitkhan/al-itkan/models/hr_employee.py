# -*- coding: utf-8 -*-
from odoo import models,fields


class PublicEmployeeInherit(models.Model):
    """redefine the field to avoid field not found issue"""
    _inherit = 'hr.employee.public'

    new_divisions = fields.Many2one('division.division', string="Division new")

class HrEmployeeExtend(models.Model):
    """redefine the field to avoid field not found issue"""

    _inherit = 'hr.employee'
    new_divisions = fields.Many2one('division.division', string="Division new")

