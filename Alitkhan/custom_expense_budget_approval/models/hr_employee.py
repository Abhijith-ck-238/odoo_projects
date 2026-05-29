# -*- coding: utf-8 -*-
from odoo import models, fields


class CustomEmployeeBaseExtend(models.AbstractModel):
    _inherit = 'hr.employee.base'

    budget_manager = fields.Many2one('hr.employee', 'Budget',
                                     domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]")


class CustomEmployeeExtend(models.Model):
    _inherit = 'hr.employee'

    budget_manager = fields.Many2one('hr.employee', string="Budget")


class CustomPublicEmployeeExtend(models.Model):
    _inherit = 'hr.employee.public'

    budget_manager = fields.Many2one('hr.employee.public', string="Budget")
