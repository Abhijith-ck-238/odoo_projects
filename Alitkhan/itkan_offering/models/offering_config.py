# -*- coding: utf-8 -*-
from markupsafe import Markup

from odoo import models, fields, api, _
from odoo.exceptions import UserError
import datetime


class OfferingConfig(models.Model):
    _name = "offering.config"
    _order = "id desc"
    _inherit = 'mail.thread'
    _description = "Config"
    _rec_name = "name"

    iq = fields.Char(string="IQ Number", required=True)
    name = fields.Char(string="Name", compute="_generate_name", store=True)
    product_id = fields.Many2one("product.product", string="Parent Product", required=True)
    parent_unit_id = fields.Many2one("access.units", string="Products Access Unit")
    child_unit_id = fields.Many2one("access.units", string="Parts Access Unit",
                                    default=lambda self: self.env['access.units'].search(
                                        [('name', 'ilike', 'spare parts')]).id)
    show_price = fields.Boolean(string="Show prices in report")
    vendor = fields.Many2one("res.partner", string="General Vendor", domain="[('is_company', '=', True)]")
    general_policy = fields.Float(string="General Policy", digits=(8, 8), default=1,
                                  groups="itkan_offering.offering_user,itkan_offering.offering_manager")
    avg_policy = fields.Float(string="Policy", digits=(8, 8),
                              groups="itkan_offering.offering_user,itkan_offering.offering_manager")
    # there is already creating date field  create_date
    # there is also already a field called create_uid for creator id
    product_bom_lines = fields.One2many("offering.config.line", "conn", string="Product Lines")
    total_vendor_price = fields.Float(compute="_get_vendor_price",
                                      groups="itkan_offering.offering_user,itkan_offering.offering_manager")
    parts_total_price = fields.Float(compute="_get_parts_total",
                                     groups="itkan_offering.offering_user,itkan_offering.offering_manager")
    config_total = fields.Float(string="Config Total",
                                groups="itkan_offering.offering_user,itkan_offering.offering_manager")
    state = fields.Selection([("draft", "Draft"), ("confirm", "Validated")], default="draft", copy=False, readonly=True)
    currency = fields.Many2one("offering.exchangerate", string="Currency", default=lambda self: self._get_us_currency())
    pack_id = fields.Many2one("product.packs.line", readonly=True)

    def copy(self, default=None):
        res = super(OfferingConfig, self.sudo()).copy(default)
        return res

    @api.depends("product_bom_lines")
    def _get_parts_total(self):
        for config in self:
            config.parts_total_price = sum(config.sudo().product_bom_lines.mapped("total_price"))

    @api.depends("product_bom_lines")
    def _get_vendor_price(self):
        for config in self:
            config = config.sudo()
            vendor_price = 0
            for line in config.product_bom_lines:
                vendor_price += line.qty * line.price_unit
            config.total_vendor_price = vendor_price

    # using an onchange and contrains functions for populate_vendor() cause onchange does not get activated
    # when pushing data from excel
    @api.onchange("vendor")
    def onchange_populate_vendor(self):
        if self.vendor:
            for item in self.product_bom_lines:
                item.vendor = self.vendor
        else:
            pass

    @api.constrains("vendor")
    def constrains_populate_vendor(self):
        if self.vendor:
            for item in self.product_bom_lines:
                if not item.vendor:
                    item.vendor = self.vendor
        else:
            pass

    # using an onchange and contrains functions for populate_policy() cause onchange does not get activated
    # when pushing data from excel
    @api.onchange("general_policy")
    def onchange_populate_policy(self):
        self = self.sudo()
        if self.general_policy:
            for item in self.product_bom_lines:
                item = item.sudo()
                item.policy = self.general_policy
        else:
            pass

    @api.constrains("general_policy")
    def constrains_populate_policy(self):
        self = self.sudo()
        if self.general_policy:
            for item in self.product_bom_lines:
                item = item.sudo()
                if not item.policy:
                    item.policy = self.general_policy
        else:
            pass

    @api.constrains("product_bom_lines")
    def calculate_config_total(self):
        total = 0
        policies = []
        for item in self.product_bom_lines:

            # removing lines with product selected
            if not item.product_id and not item.smn:
                item.unlink()
                continue

            total += item.total_price
            policies.append(item.policy)
        self.sudo().config_total = total
        try:
            self.sudo().avg_policy = sum(policies) / len(policies)
        except ZeroDivisionError:
            self.sudo().avg_policy = 1

    def _get_us_currency(self):
        currency_id = self.env['offering.exchangerate'].search([("currency_name", "=", "USD")])
        if currency_id:
            return currency_id.id if currency_id else False

    def confirm_config(self):

        if not self.currency:
            raise UserError(_("Please select a currency before confirming"))

        elif not self.parent_unit_id or not self.child_unit_id:
            raise UserError(_("You Need To Fill The Access Unit Fields Before Confirming The Configuration"))

        else:
            if not self.product_id.unit_id:
                self.product_id.unit_id = self.parent_unit_id.id
            else:
                pass

            for line in self.product_bom_lines:
                if not line.vendor:
                    raise UserError(f"Line {line.product_id.display_name} doesn't have a selectd vendor")

                if not line.product_id.unit_id:
                    line.product_id.unit_id = self.child_unit_id.id

            if self.pack_id:
                self.pack_id.unlink()

            values = {
                "name": self.iq + ' Pack',
                "product_id": self.product_id.id,
                "product_lines": [],
            }

            for line in self.product_bom_lines:
                values["product_lines"].append((0, 0, {
                    "product_id": line.product_id.id,
                    "qty_uom": line.qty,
                    "unit_price": line.total_price / line.qty,
                }))
            pack_id = self.env["product.packs.line"].create(values)
            self.pack_id = pack_id.id

            # body_message = f"""The configuration is approved by <a href="#" data-oe-model="res.users" data-oe-id="{self.env.user.id}">{self.env.user.name}</a>"""
            body_message = Markup((
                                    '<a href="#" data-oe-model="res.users" data-oe-id="%s">'
                                      "%s"'</a>'
                                  ) % (self.env.user.id, self.env.user.name))

            self.message_post(
                body='The configuration is approved by ' + body_message,
                message_type='notification',
                subtype_xmlid='mail.mt_comment',
                partner_ids=[self.create_uid.partner_id.id])

            self.state = "confirm"

    def reset_to_draft(self):
        self.state = "draft"

    @api.constrains("iq", "product_id")
    def _generate_name(self):
        self.name = str(self.product_id.name) + "-" + str(self.iq)

    def recalculate_button(self):
        context = dict(self.env.context)
        if context.get("related_offering_line"):
            offering_line_id = self.env['offering.offering.line'].browse([context['related_offering_line']])
            # offering_line_id.config = self.id
            offering_line_id.calculcate_sheet()


class OfferingConfigLine(models.Model):
    _name = "offering.config.line"
    _description = "config record model bom line items model"
    _rec_name = "product_id"

    conn = fields.Integer()  # kept it justt incase saeb used it somewhere
    optional_product = fields.Boolean(string="Optional")
    product_id = fields.Many2one("product.product", string="Product")
    smn = fields.Char(string="Part No.")
    description = fields.Char(string="Description")
    vendor = fields.Many2one("res.partner", string="Vendor")
    qty = fields.Integer(string="Quantity", default=1)
    price_unit = fields.Float(string="Unit Price", default=1,
                              groups="itkan_offering.offering_user,itkan_offering.offering_manager")
    policy = fields.Float(string="Policy", default=1, digits=(8, 8),
                          groups="itkan_offering.offering_user,itkan_offering.offering_manager")
    total_price = fields.Float(string="Total Price",
                               groups="itkan_offering.offering_user,itkan_offering.offering_manager")
    temp_product_name = fields.Char(string="Temporary Product Name")
    long_desc = fields.Text(string="Product Long Description")
    is_defect = fields.Boolean("Is Defect?")

    @api.onchange("product_id")
    def add_product_name(self):
        for line in self:
            if line.product_id.name:
                line.description = line.product_id.name
            else:
                pass

    @api.onchange("product_id")
    def get_smn(self):
        for item in self:
            if item.product_id:
                item.smn = item.product_id.default_code

    @api.depends("qty", "price_unit", "policy")
    def _calc_total(self):
        for rcd in self:
            rcd.sudo().total_price = rcd.qty * rcd.price_unit * rcd.policy

    @api.constrains('smn', 'temp_product_name')
    def _get_product(self):
        for rcd in self:
            # for product with part number
            if rcd.smn:
                product_id = self.env['product.product'].search([('default_code', '=', rcd.smn)])
                if len(product_id) > 1:
                    raise UserError(_(f"Detected two products with the same SMN [{rcd.smn}], please fix this issue"))
                elif len(product_id) == 1:
                    rcd.product_id = product_id.id
                else:
                    new_product_id = self.env['product.product'].create({
                        'name': rcd.temp_product_name if rcd.temp_product_name else "No product, Please Create",
                        'default_code': rcd.smn,
                        'type': 'consu',
                        'product_long_desc': rcd.long_desc if rcd.long_desc else False,
                    })
                    rcd.product_id = new_product_id.id
                    rcd.long_desc = False

            # for products without part number
            elif rcd.temp_product_name:
                product_id = self.env['product.product'].search(
                    [('name', '=', rcd.temp_product_name), ('default_code', '=', False)])
                if len(product_id) > 1:
                    raise UserError(_(f"Detected two products with the same name [{rcd.name}], please fix this issue"))
                elif len(product_id) == 1:
                    rcd.product_id = product_id.id
                else:
                    new_product_id = self.env['product.product'].create({
                        'name': rcd.temp_product_name,
                        'type': 'consu',
                    })
                    rcd.product_id = new_product_id.id
            else:
                pass


class MrpBom(models.Model):
    _inherit = "mrp.bom"

    config_id = fields.Many2one("offering.config", readonly=True)
