# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError

class AccessUnits(models.Model):
    _name = 'access.units'
    name = fields.Char(string="Access Unit Name")

class AccessUnits(models.Model):
    _name = "access.units.line"

    unit_id = fields.Many2one('access.units', required=True)
    show_cost_price = fields.Boolean()
    show_sales_price = fields.Boolean()
    employee_id = fields.Many2one('hr.employee')

class AccessUnitsProducts(models.Model):
    _inherit="product.template"
    unit_id = fields.Many2one('access.units',string="Product Access Units")
    show_sales_price = fields.Boolean(compute="_get_access_unit")
    show_cost_price = fields.Boolean(compute="_get_access_unit")

    def _get_access_unit(self):
        user = self.env.user
        for product in self:
            if user.has_group('access_units.access_unites_limited_users'):
                unit_line_id = user.employee_id.access_units_line.search([('unit_id', '=', product.unit_id.id), ('employee_id', '=', user.employee_id.id)])
                if unit_line_id:
                    product.show_cost_price = unit_line_id.show_cost_price
                    product.show_sales_price = unit_line_id.show_sales_price
                else:
                    product.show_cost_price = False
                    product.show_sales_price = False
            else:
                product.show_cost_price = True
                product.show_sales_price = True
                


class AccessUnitsEmployees(models.Model):
    _inherit="hr.employee"
    
    # This field is necesary for apply record rules
    access_units = fields.Many2many('access.units', string="Employee Access Units", readonly=True) 
    access_units_line = fields.One2many('access.units.line', 'employee_id',string="Employee Access Units")

    @api.constrains('access_units_line')
    def add_units(self):
        unit_ids = []
        if self.access_units_line:
            for line in self.access_units_line:
                unit_ids.append(line.unit_id.id)
            self.write({
                'access_units': [(6, 0, unit_ids)]
            })

class AccessUnitsSales(models.Model):
    _inherit="sale.order"

    access_unit_ids = fields.Many2many('access.units', string="Access Units")

    @api.constrains('order_line')
    def _get_access_unit(self):
        for sale_order in self:
            units_ids = []
            for line in sale_order.order_line:
                if line.product_id.unit_id.id != False and line.product_id.unit_id.id not in units_ids:
                    units_ids.append(line.product_id.unit_id.id)
                else:
                    pass
            if units_ids:
                sale_order.write({'access_unit_ids': [(6, 0, units_ids)] })
            else:
                pass



class AccessUnitsPurchase(models.Model):
    _inherit="purchase.order"

    access_unit_ids = fields.Many2many('access.units',string="Access Units")
    @api.constrains('order_line')
    def _get_access_unit(self):
        for purchase_order in self:
            units_ids = []
            for line in purchase_order.order_line:
                if line.product_id.unit_id.id != False and line.product_id.unit_id.id not in units_ids:
                    units_ids.append(line.product_id.unit_id.id)
                else:
                    pass
            
            if units_ids:
                purchase_order.write({'access_unit_ids': [(6, 0, units_ids)]})
            else:
                pass