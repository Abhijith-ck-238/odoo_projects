# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from datetime import datetime, timedelta
from odoo.exceptions import UserError
from odoo.tools import float_is_zero, float_compare, DEFAULT_SERVER_DATETIME_FORMAT
from odoo import SUPERUSER_ID


class ProductPack(models.Model):
	_name = 'product.pack'
	_description = "Product Pack"
	
	product_id = fields.Many2one(comodel_name='product.product', string='Product', required=True)
	qty_uom = fields.Float(string='Quantity', required=True, defaults=1)
	unit_price = fields.Float(groups="itkan_offering.offering_user")
	total_price = fields.Float(compute="_get_total_price",groups="itkan_offering.offering_user")
	uom_id = fields.Many2one(related='product_id.uom_id', string="Unit of Measure", readonly=True)
	name = fields.Char(related='product_id.name', readonly=True)
	line_id = fields.Many2one('product.packs.line')

	@api.onchange("product_id")
	def _get_list_price(self):
		for line in self:
			line.unit_price = line.product_id.list_price
			line.qty_uom = 1

	@api.onchange("qty_uom" ,"unit_price")
	def _get_total_price(self):
		for line in self:
			line.total_price = line.qty_uom * line.unit_price


class ProductPacksLines(models.Model):
	_name = "product.packs.line"
	name = fields.Char()
	product_lines = fields.One2many('product.pack', 'line_id')
	product_id = fields.Many2one("product.product", required=True)
	price = fields.Float(string="Total Price", compute="_get_list_price",groups="itkan_offering.offering_user")

	@api.onchange("product_lines")
	def _get_list_price(self):
		for line in self:
			total_price = 0
			for product in line.product_lines:
				total_price += product.total_price
			line.price = total_price


class ProductProduct(models.Model):
	_inherit = 'product.product'

	pack_lines = fields.One2many('product.packs.line', 'product_id')