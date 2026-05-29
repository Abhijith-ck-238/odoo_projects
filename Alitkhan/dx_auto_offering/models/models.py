# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import UserError
import n2w


class AutoOfferingQuotation(models.Model):
    _name = 'quotation.offer'
    _description = 'Auto Offers'

    name = fields.Char(string="Number", required=True, copy=False,
                       readonly=True, index=True, default='New')

    _status = [('draft', 'draft'), ('confirmed', 'Confirmed'),
               ('canceled', 'Canceled')]
    status = fields.Selection(_status, default='draft')

    customer_id = fields.Many2one('res.partner', string='Customer',
                                  required=True)
    iq_number = fields.Char(string='IQ Number')
    reference = fields.Char(string='Reference')
    offer_date = fields.Date(string='Offer Date', required=True)

    company_id = fields.Many2one('res.company', 'Company', required=True,
                                 index=True,
                                 default=lambda self: self.env.company,
                                 readonly=True)

    line_ids = fields.One2many('quotation.offer.line', 'line_id',
                               string="Offer Lines")

    total_offer_price = fields.Monetary(compute="_compute_calculation",
                                        currency_field='currency_id',
                                        store=True)
    written_total_offer_price = fields.Char(compute="_compute_calculation")
    total_net_price = fields.Monetary(compute="_compute_calculation",
                                      currency_field='currency_id', store=True,
                                      string="Total Cost")
    package_policy = fields.Float(compute="_compute_calculation", readonly=True,
                                  store=True)
    profit = fields.Monetary(compute="_compute_calculation",
                             currency_field='currency_id', readonly=True,
                             store=True)

    exchange = fields.Float()
    currency_id = fields.Many2one('res.currency', string='currency',
                                  default=lambda
                                      self: self.env.company.currency_id.id)

    subject = fields.Char(string="Subject")
    sincerely_ids = fields.Many2many('hr.employee.public')
    printing_string = fields.Html(compute="_compute_report")

    template_id = fields.Many2one('quotation.offer.template', string='template')

    @api.model
    def create(self, values):
        values['name'] = self.env['ir.sequence'].next_by_code(
            'quotation.offer.code')
        res = super(AutoOfferingQuotation, self).create(values)
        return res

    @api.onchange('currency_id')
    def on_currency_change(self):
        for rec in self:
            if rec.currency_id:
                for line in rec.line_ids:
                    line.offer_currency_id = rec.currency_id.id

    @api.constrains('currency_id', 'line_ids')
    def set_currency_change(self):
        for rec in self:
            if rec.currency_id:
                for line in rec.line_ids:
                    line.offer_currency_id = rec.currency_id.id

    @api.depends('line_ids', 'currency_id')
    def _compute_calculation(self):
        for rec in self:
            temp_total_offer_price = 0
            temp_total_net_price = 0
            for line in rec.line_ids:
                temp_total_offer_price += line.offer_total_price
                temp_total_net_price += line.total_net_price * line.exchange_rate
            rec.total_offer_price = temp_total_offer_price
            rec.total_net_price = temp_total_net_price
            rec.package_policy = 0 if temp_total_net_price == 0 else temp_total_offer_price / temp_total_net_price
            rec.profit = temp_total_offer_price - temp_total_net_price
            rec.written_total_offer_price = n2w.convert(
                int(temp_total_offer_price))

    @api.depends("template_id")
    def _compute_report(self):
        fields = [
            "customer_id.name",
            "iq_number",
            "reference",
            "offer_date",
            "total_offer_price",
            "total_net_price",
            "package_policy",
            "profit",
            "exchange",
            "currency_id.name",
            "printing_string",
            "template_id",
            "written_total_offer_price"
        ]

        for rec in self:
            # Early return if no template
            if not rec.template_id:
                rec.printing_string = ""
                continue

            # Start with template or empty string
            current_printing_string = rec.template_id.template or ""

            for field in fields:
                # Split nested fields
                fields_to_access = field.split(".")

                # Initialize current value with record
                current_value = rec

                # Traverse nested fields safely
                for field_to_access in fields_to_access:
                    # Safe navigation: stop if any intermediate value is False/None
                    if current_value is False or current_value is None:
                        current_value = ""
                        break

                    # Get the next level of value
                    current_value = current_value[field_to_access]

                # Convert to string, defaulting to empty string
                current_value = str(
                    current_value) if current_value is not None else ""

                # Replace placeholder in template
                current_printing_string = current_printing_string.replace(
                    "{" + field + "}",
                    current_value
                )

            rec.printing_string = current_printing_string

    def action_confirm(self):
        for rec in self:
            rec.status = 'confirmed'

    def action_cancel(self):
        for rec in self:
            rec.status = 'canceled'

    def action_draft(self):
        for rec in self:
            rec.status = 'draft'


class AutoOfferingQuotationLine(models.Model):
    _name = 'quotation.offer.line'
    _description = 'Auto Offers Lines'

    line_id = fields.Many2one('quotation.offer')

    product_category = fields.Many2one('product.category', string='Category',
                                       required=True)
    product_id = fields.Many2one('product.product', string='Product',
                                 required=True)
    part_number = fields.Char(string="Part Number",
                              related="product_id.default_code")
    description = fields.Char(string="Description")
    quantity = fields.Float(default=1)
    policy = fields.Float(default=1)
    discount = fields.Float()
    unit_net_price = fields.Float(default=1)
    currency_id = fields.Many2one('res.currency', string='Currency',
                                  required=True)
    offer_currency_id = fields.Many2one('res.currency', string='Offer Currency',
                                        readonly=True)
    exchange_rate = fields.Float(string="Exchange Rate", default=1.0,
                                 digits=(5, 5), compute="get_exchange_rate",
                                 inverse="get_exchange_rate", store=True)
    total_net_price = fields.Float(compute="_compute_calculations")
    unit_price_bd = fields.Float(compute="_compute_calculations",
                                 string='Unit Price Before Discount')
    total_price_bd = fields.Float(compute="_compute_calculations",
                                  string='Total Price Before Discount')
    offer_unit_price = fields.Float(compute="_compute_calculations")
    offer_total_price = fields.Float(compute="_compute_calculations")

    @api.depends('product_id', 'quantity', 'policy', 'discount',
                 'unit_net_price', 'exchange_rate')
    def _compute_calculations(self):
        for rec in self:
            rec.total_net_price = rec.unit_net_price * rec.quantity
            rec.unit_price_bd = rec.unit_net_price * rec.policy * rec.exchange_rate
            rec.total_price_bd = rec.unit_net_price * rec.policy * rec.exchange_rate * rec.quantity
            rec.offer_unit_price = rec.unit_net_price * rec.policy * rec.exchange_rate * (
                    (100 - rec.discount) / 100)
            rec.offer_total_price = rec.unit_net_price * rec.policy * rec.exchange_rate * rec.quantity * (
                    (100 - rec.discount) / 100)

    @api.onchange('product_id')
    def create_description(self):
        for rec in self:
            rec.description = rec.product_id.name

    @api.depends('currency_id', 'offer_currency_id')
    def get_exchange_rate(self):
        for rec in self:
            if rec.currency_id and rec.offer_currency_id:
                res_currency = self.env['res.currency']._get_conversion_rate(
                    rec.offer_currency_id, rec.currency_id, self.env.company,
                    fields.Date.today())
                rec.exchange_rate = 1 / res_currency
            else:
                rec.exchange_rate = 1.0


class AutoOfferingReportTemplate(models.Model):
    _name = 'quotation.offer.template'

    name = fields.Char()
    template = fields.Html()
