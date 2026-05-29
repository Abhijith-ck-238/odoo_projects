# -*- coding: utf-8 -*-

from odoo import models, fields, api


class ProductTemplateExt(models.Model):

    _inherit = "product.template"

    hierarchy = fields.Many2one("products.hierarchy",string="Hierarchy")
    parent_product = fields.Many2many(comodel_name="product.template",relation="accessory_parent_rel",
    column1="parent",column2="accessory",string="Parent Product")
    zone = fields.Many2one("products.hierarchyzone",string="Zone")










class ProductsHierarchy(models.Model):

    _name = "products.hierarchy"

    name = fields.Char(string="Category name")



class ProductHierarchyZone(models.Model):
    _name="products.hierarchyzone"

    name = fields.Char(string="Zone")