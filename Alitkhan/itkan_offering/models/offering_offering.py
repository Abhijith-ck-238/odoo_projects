# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
import re
import datetime
from odoo.exceptions import UserError



class OfferingOffering(models.Model):
	_name = "offering.offering"
	_inherit =  'mail.thread'
	_order = "id desc"
	_description = "Offering"

	CONTRACT_CATEG = [("private","Private"),("governmental","Governmental")]

	name=fields.Char(readonly=True)
	ref_number = fields.Char(string="Reference Number")
	customer = fields.Many2one("res.partner",string="Customer")
	product_lines = fields.One2many("offering.offering.line","conn",string="Product Lines")
	region = fields.Many2one("offering.region",string="Region")
	offer_currency = fields.Many2one("res.currency",string="Offer Currency")
	price_list = fields.Many2one("product.pricelist",string="Offer Pricelist")
	total_price_in_usd = fields.Float(string="Total Price in USD", compute="_get_total_usd_price", groups="itkan_offering.offering_user, itkan_offering.offering_manager")
	total_price_in_iqd = fields.Float(string="Total Price in IQD", compute="_get_total_usd_price", groups="itkan_offering.offering_user, itkan_offering.offering_manager")
	access_unit_ids = fields.Many2many('access.units',relation="access_offering_rel",column1="access_offer",column2="offer_access",string="Access Units")
	project_policy = fields.Float(string="Project Policy", compute="_get_project_policy_and_cost" )
	total_cost = fields.Float("Total Cost", compute="_get_project_policy_and_cost")
	category = fields.Selection([("Governmental","governmental"),("private","Private")],string="Offer Category")
	""" Contract Fields """
	iq = fields.Char(string="IQ Number")
	contract_no = fields.Char(string="Contract Number")
	sign_date = fields.Date(string="Signing Date")
	contract_type = fields.Selection(CONTRACT_CATEG,string="Category")
	related_contract = fields.Many2one("contract.contract",string="Related Contract",readonly=True, copy=False)
	contract_created = fields.Boolean(default=False, copy=False)
	signed_by = fields.Many2one("res.partner",string="signed_by")
	""" sale order fields"""
	related_sale_order = fields.Many2one("sale.order",string="Related Sale Order",readonly=True, copy=False)
	managerial_approval = fields.Boolean()
	state = fields.Selection([("draft","Draft"),("approved","Approved"),("cancelled","Cancelled")], default="draft", copy=False)

	company_id = fields.Many2one("res.company", readonly=True, copy=False, default=lambda self: self.env.company.id)
	sp_and_labor = fields.Char(string="SP. + Labor")
	labor = fields.Char(string="Labor")
	site_prep = fields.Char(string="Site Prep")
	training = fields.Char(string="Training")
	payment_method = fields.Char(string="Payment Method")
	incoterms = fields.Char(string="Incoterms")
	additional = fields.Text(string="Additional")
	summary = fields.Char(string="Summary")

	sale_order_created = fields.Boolean(default=False, copy=False)
	purchase_order_ids = fields.One2many('purchase.order', 'related_offering_record', readonly=True, copy=False, groups="purchase.group_purchase_user")
	purchase_order_created = fields.Boolean(default=False, copy=False)





	""" Report Templates """
	vendor_id = fields.Many2one("res.partner", string="Report Vendor", help="The vendor that will be printed with offer's PDF")
	project_name = fields.Char()
	company_report = fields.Many2one('res.company', string="Offer Company", default= lambda self: self.env.company.id, help="The Comapny in which this offer will printed as")
	tendor_no = fields.Char(string="Tender No")
	project_subject = fields.Char()
	ifb_no = fields.Char(string="IFB no")
	offer_date = fields.Date(help="The date printed on this offer's PDF")
	add_conditions_and_warranty = fields.Boolean(string="Add Conditions & Warranty", help="To decide whether you want to print the \"Condiitions & Warranty ...\" section in the report. This one is mainly for Siemense Offers")
	add_refer_to_our_enclosed_offer = fields.Boolean(string="Add Refer To Our Enclosed Offer Section", help="To decide whether you want to print the \"Please refer to our enclosed offer...\" section in the offer's report")
	terms_and_conditions_section_id = fields.Many2one("offering.template", string="Terms & Conditions Section", domain="[('sections', '=', 'terms_and_conditions')]", help="the first line print in \"Term & Condition\" Section")
	include_section_id = fields.Many2one("offering.template", domain="[('sections', '=', 'include')]", help="The \"Include :\" section that is printed in the in the Summary List table")
	sincerely_ids = fields.Many2many("hr.employee.public", relation="hr_offer_rel", column1="hr_offer", column2="offer_hr", help="The name of the employees printed at the end of the first page")
	report_templates = [
		(0, 0, {'name': 'Intorduction', 'sections': 'intro'}),
		(0, 0, {'name': 'Prices', 'sections': 'prices'}),
		(0, 0, {'name': 'Way Of Shipment', 'sections': 'shipment'}),
		(0, 0, {'name': 'Correspondence Bank', 'sections': 'bank'}),
		(0, 0, {'name': 'Special Conditions for Software', 'sections': 'software_conditions'}),
		(0, 0, {'name': 'Installation', 'sections': 'install'}),
		(0, 0, {'name': 'Country of Origin and Delivery Time', 'sections': 'origin_delivery'}),
		(0, 0, {'name': 'Reservation of Offer/Performa- Invoice', 'sections': 'reserve'}),
		(0, 0, {'name': 'Term of Payment', 'sections': 'terms'}),
		(0, 0, {'name': 'Warranty', 'sections': 'warranty'}),
		(0, 0, {'name': 'Certificate of Origin', 'sections': 'cetrificate_of_origin'}),
		(0, 0, {'name': 'Price Validity', 'sections': 'price'}),
		(0, 0, {'name': 'Force Majeure', 'sections': 'force'}),
	]
	report_template_lines = fields.One2many('offering.template.line', 'offering_id', default=report_templates)

	def check_defect(self):
		lines = self.product_lines.config.mapped('product_bom_lines.is_defect')
		return any(lines)

	@api.depends('product_lines')
	def _get_project_policy_and_cost(self):
		for offer in self:
			final_unit_price_usd_sum, vendor_price_sum  = 0, 0
			for line in offer.product_lines:
				final_unit_price_usd_sum += line.final_unit_price_usd
				vendor_price_sum += line.vendor_price
			offer.total_cost = vendor_price_sum
			try:
				offer.project_policy = final_unit_price_usd_sum / vendor_price_sum
			except ZeroDivisionError:
				offer.project_policy = 0

	@api.constrains('product_lines')
	def _get_access_unit(self):
			for offer in self:
					units_ids = []
					for line in offer.product_lines:
							if line.product_id.unit_id and line.product_id.unit_id.id not in units_ids:
									units_ids.append(line.product_id.unit_id.id)
							else:
									pass

					if units_ids:
						offer.write({'access_unit_ids': [(6, 0, units_ids)]})
					else:
						pass

	@api.depends("product_lines")
	def _get_total_usd_price(self):
		for offer in self:
				offer.total_price_in_usd = sum(offer.product_lines.mapped("final_total_price_usd"))
				offer.total_price_in_iqd = sum(offer.product_lines.mapped("final_total_price_iqd"))

	@api.constrains("customer","ref_number")
	def compute_name (self):
		if self.customer:
			self.name = self.customer.name + "-" + str(self.ref_number)
		else:
			self.name = (self.ref_number)

	def cancel_offer(self):
		if self.related_sale_order:
			self.related_sale_order.action_cancel()
		if self.purchase_order_ids:
			self.purchase_order_ids.button_cancel()
		self.state="cancelled"
		self.message_post(
					body="Offer was cancelled by %s" % self.env.user.name,
					message_type='notification',
					subtype_xmlid='mail.mt_comment',
					partner_ids= [self.create_uid.partner_id.id])


	def reset_to_draft(self):
			self.state="draft"
			self.purchase_order_created = False
			self.message_post(
						body="Offer was reset  by %s" %self.env.user.name,
						message_type='notification',
						subtype_xmlid='mail.mt_comment',
						partner_ids= [self.create_uid.partner_id.id])

	def approve_offer(self):
			self.managerial_approval = True
			self.state = "approved"
			self.message_post(
						body="Offer was approved  by %s" %self.env.user.name,
						message_type='notification',
						subtype_xmlid='mail.mt_comment',
						partner_ids= [self.create_uid.partner_id.id])


	def create_sale_order(self):
			if not self.customer:
				raise UserError(_("Please set a customer before creating a sale order"))
			if not self.product_lines:
				raise UserError (_("product lines are empty"))
			ensure_none = self.env["sale.order"].search([("related_offering_record","=",self.id)])
			if ensure_none :
				raise UserError(_("Sorry, You cant create a new sale order because a sale order already exists with this records as a parent,please delete it first"))
			sale_order_vals = {
					"partner_id":self.customer.id,
					"related_offering_record":self.id,
					"state":"draft",
					"pricelist_id":self.price_list.id,
					"project_num": self.iq
				}
			list_of_line_contents=[]
			for item in self.product_lines:
					list_of_line_contents.append((0,0,{
							"product_id":item.product_id.id,
							"sale_pack_id": item.config.pack_id.id,
							"price_unit": item.final_unit_price_usd if self.offer_currency.name == "USD" else item.final_unit_price_iqd,
							"product_uom_qty":item.qty,
							"currency_id":self.offer_currency.id,
						}))
					sale_order_vals["order_line"] = list_of_line_contents
			sale_order_id = self.env["sale.order"].create(sale_order_vals)
			if sale_order_id:
				self.sale_order_created = True
				self.related_sale_order = sale_order_id
			else:
				raise UserError (_("Sale Order Was Not Created For Some Reason"))



	def create_purchase_order(self):
			if not self.product_lines:
				raise UserError (_("product lines are empty"))

			# dicstionay data: {vendor_id: vendor_currency }
			vendors = {}
			for offering_line in self.product_lines:
				# fetching the currency record because the saved one within the config is not from res.currency
				res_currency_id = self.env['res.currency'].search([('name', '=', offering_line.config.currency.currency_name )])
				for config_line in offering_line.config.product_bom_lines:
					# if vendor is not in dict
					if not vendors.get( config_line.vendor.id ):
						vendors[ config_line.vendor.id ] = res_currency_id.id

					#  if vendor is in dict but currency is different
					elif vendors.get( config_line.vendor.id ) and vendors.get( config_line.vendor.id ) != res_currency_id.id:
						raise UserError("Detected two currencies for the same vendor")

					#  if vendor is in dict and currency is the same
					else:
						pass

			for vendor_id, currency_id in vendors.items():
				purchase_order_vals = {
					"partner_id": vendor_id,
					"origin": self.name,
					"currency_id": currency_id,
					"related_offering_record":self.id,
					"date_planned":datetime.datetime.now()
				}

				list_of_line_contents=[]
				for line in self.product_lines.config.product_bom_lines:
						if line.vendor.id == vendor_id:
							#   for item in product.config.product_bom_lines:
							list_of_line_contents.append((0,0,{"product_id":line.product_id.id,"price_unit": line.price_unit,"product_qty":line.qty,"name":line.product_id.name,"product_uom":line.product_id.uom_id.id}))
				purchase_order_vals["order_line"] = list_of_line_contents
				#raise UserError (_(str(purchase_order_vals)))
				purchase_order_id = self.env["purchase.order"].create(purchase_order_vals)
				self.purchase_order_ids += purchase_order_id

			self.purchase_order_created = True


	def create_contract(self):
			if self.confirm_contract_data():
				ensure_none = self.env["contract.contract"].search([("related_offering_record","=",self.id)])
				if ensure_none:
						raise UserError (_("Sorry, you cannot create a contract as a contract already exists with this record as a parent"))
				contract_vals = {
					"partner_id":self.customer.id,
					"related_offering_record":self.id,
					"iq":self.iq,
					"number":self.contract_no,
					"signed_date":self.sign_date,
					"contract_categ":self.contract_type,
					"contract_signed_by":self.signed_by.id
					}
				list_of_line_contents=[]
				for item in self.product_lines:
						list_of_line_contents.append((0,0,{"product_id":item.product_id.id,"price": item.unit_price,"qty":item.qty}))
						contract_vals["product_lines"] = list_of_line_contents
						contract_id = self.env["contract.contract"].create(contract_vals)
						if contract_id:
							self.contract_created = True
							self.related_contract = contract_id
						else:
							raise UserError (_("Contract Was Not Created For Some Reason"))
						# raise UserError("booo")
			else:
				raise UserError (_("One or more mandatory Contract fields has no value"))

	def confirm_contract_data(self):
			if self.customer.id and self.iq and self.contract_no and self.sign_date:
					return True
			else:
					return False

	def view_contracts(self):
			return {
					'type': 'ir.actions.act_window',
					'name': 'Contract',
					'res_model': 'contract.contract',
					'views': [(False, 'form')],
					'res_id': self.related_contract.id,
			}

	def view_purchase_orders(self):
			return {
					'type': 'ir.actions.act_window',
					'name': 'Offering Purchase Order',
					'view_type': 'form',
					'view_mode': 'list',
					'res_model': 'purchase.order',
					'views': [(False,'list'),(False, 'form')],
					'domain': [('related_offering_record', '=', self.id)],
					'target': 'current',
			}


class OfferingOfferingLine(models.Model):
		_name="offering.offering.line"
		name = fields.Char(string="Description")



		conn=fields.Integer()
		optional_product = fields.Boolean(string="Optional")
		hide_from_offer_report = fields.Boolean(string="Hide", help="check if you want to hide this line in the printed report")
		product_id = fields.Many2one("product.product",string="Product")
		vendor = fields.Many2one("res.partner",related="config.vendor",string="Vendor")
		config = fields.Many2one("offering.config", name="Config", ondelete="restrict")
		config_currency = fields.Many2one(related="config.currency",string="Config Currency")
		currency = fields.Many2one("offering.exchangerate",string="Currency")
		exchange_rate_1 = fields.Float(related="currency.exchange_rate",string="Exchange rate")
		qty = fields.Integer(string="Quantity",default=1)
		policy = fields.Float(string="avg. Policy",default=1, digits = (8, 8))
		config_net_price = fields.Float(string="Config Price", related="config.parts_total_price")
		vendor_price = fields.Float(string="Net Price (Vendor Price)", related="config.total_vendor_price", groups="itkan_offering.offering_user,itkan_offering.offering_manager")
		unit_price = fields.Float(string="USD Unit Price", readonly=False)
		total_price = fields.Float(string="USD Total Price", readonly=True)
		discount=fields.Float(string="Discount")
		price_unit_after_discount = fields.Float(string="Unit Price After Discount", readonly=True)
		price_total_after_discount = fields.Float(string="Total Price After Discount", readonly=True)
		offer_unit_price = fields.Float(string="Offer Unit Price", readonly=True)
		offer_total_price = fields.Float(string="Offer Total Price", readonly=True)
		offer_unit_iqd = fields.Float(string="Offer Unit Price In IQD", readonly=True)
		offer_total_iqd = fields.Float(string="Offer Total Price In IQD", readonly=True)
		misc = fields.Float(string="+/-")
		final_unit_price_usd = fields.Float(string="Final Unit Price USD")
		final_total_price_usd = fields.Float(string="Final Total Price USD", readonly=True)
		final_unit_price_iqd = fields.Float(string="Final Unit Price IQD", readonly=True)
		final_total_price_iqd = fields.Float(string="Final Total Price IQD", readonly=True)
		budget_unit_price = fields.Float(string="Budget Unit Price")
		budget_total_price = fields.Float(string="Budget Total Price")
		exchange_rate = fields.Float(string="Exch. $-IQD")
		config_policy_defined = fields.Boolean(compute="_compute_config_policy_defined")


		@api.depends("config")
		def _compute_config_policy_defined(self):
			for item in self:
				item = item.sudo()
				if item.config:
					if item.config.avg_policy:
						item.config_policy_defined = True
					else:
						item.config_policy_defined = False

				else:
					item.config_policy_defined = False

		@api.onchange("product_id")
		def _get_product_name(self):
				for line in self:
						if line.product_id:
								line.name = line.product_id.display_name
						else:
								pass

		@api.onchange("budget_unit_price","qty")
		def calculate_budget_total_price(self):
				for item in self:
						item = item.sudo()
						item.budget_total_price = item.budget_unit_price * item.qty


		@api.constrains("config")
		def assign_product(self):
				for item in self:
						item = item.sudo()
						if item.config and not item.product_id:
								item.product_id = item.config.product_id
								item.currency = item.config.currency
								item.unit_price = item.config.config_total * item.config.currency.exchange_rate if item.config.currency.exchange_rate else 1
								item.policy = item.config.avg_policy #added
								item.total_price = item.config.config_total * item.qty * item.config.currency.exchange_rate
								item.price_unit_after_discount = item.config.config_total * item.config.currency.exchange_rate
								item.price_total_after_discount = item.config.config_total * item.qty * item.config.currency.exchange_rate
								item.offer_unit_price = item.config.config_total * item.config.currency.exchange_rate
								item.offer_total_price = item.config.config_total * item.qty * item.config.currency.exchange_rate
								item.final_unit_price_usd = item.config.config_total * item.config.currency.exchange_rate
								item.final_total_price_usd = item.config.config_total * item.qty * item.config.currency.exchange_rate

		@api.onchange("config", "exchange_rate", "exchange_rate_1", "unit_price", "qty", "discount")
		def calculcate_sheet(self):
			for item in self:
					unit_price = item.config_net_price * (item.exchange_rate_1 if item.exchange_rate_1 else 1)
					item.policy = item.config.avg_policy #added
					item.currency = item.config.currency
					item.unit_price = unit_price
					item.total_price = unit_price * item.qty
					if item.discount:
							discount = 1- (item.discount / 100)
					else:
							discount = 1
					price_unit_after_discount = unit_price * discount
					item.price_unit_after_discount = price_unit_after_discount
					item.price_total_after_discount = price_unit_after_discount * item.qty
					item.offer_unit_price = price_unit_after_discount * 1
					item.offer_total_price = price_unit_after_discount * item.qty

					offer_unit_iqd =  price_unit_after_discount * (item.exchange_rate if item.exchange_rate else 1)
					item.offer_unit_iqd = offer_unit_iqd
					item.offer_total_iqd = offer_unit_iqd * item.qty

					if item.misc:
							misc = (1 + item.misc/100)
					else:
							misc = 1
					final_unit_price_usd = price_unit_after_discount * misc
					item.final_unit_price_usd = final_unit_price_usd
					item.final_total_price_usd = final_unit_price_usd * item.qty

					item.final_unit_price_iqd = final_unit_price_usd * item.exchange_rate
					item.final_total_price_iqd = final_unit_price_usd * item.exchange_rate * item.qty

		def edit_calculation_action(self):
			context = dict(self.env.context)
			context["form_view_ref"] = "itkan_offering.offering_config_form_calculcation"
			context["related_offering_line"] = self.id
			return {
				"name": "Edit Calculation",
				"type": "ir.actions.act_window",
				"res_model": "offering.config",
				"views": [[False, "form"]],
				"res_id": self.config.id,
				"context": context,
				"target": 'new',
			}

class OfferingSaleOrder(models.Model):
		_inherit = "sale.order"

		related_offering_record = fields.Many2one("offering.offering",string="Related Offering Record",readonly=True, ondelete="restrict")

class OfferingPurchaseOrder(models.Model):

		_inherit = "purchase.order"

		related_offering_record = fields.Many2one("offering.offering",string="Related Offering Record",readonly=True)


class OfferingContractRec(models.Model):
		_inherit="contract.contract"

		related_offering_record = fields.Many2one("offering.offering",string="Related Offering Record",readonly=True)

class OfferingProductRec(models.Model):
		_inherit="contract.product"

		price = fields.Float(groups="itkan_offering.offering_user")

class OfferingRegions(models.Model):
		_name="offering.region"
		_rec_name="name"

		name=fields.Char(string="Region")
