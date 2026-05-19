# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError
import datetime, re

class OfferingTemplate(models.Model):
    _name = "offering.template"
    _rec_name = "name"

    name = fields.Char(required=True)
    body = fields.Html(help="Wrap the fields you want in the report with curly braces { }", required=True)
    sections = fields.Selection([
        ('intro', 'Intorduction'),
        ('prices', 'Prices'),
        ('shipment', 'Way Of Shipment'),
        ('bank', 'Correspondence Bank'),
        ('software_conditions', 'Special Conditions for Software'),
        ('install','Installation'),
        ('origin_delivery', 'Country of Origin and Delivery Time'),
        ('reserve', 'Reservation of Offer/Performa- Invoice'),
        ('terms', 'Term of Payment'),
        ('warranty', 'Warranty'),
        ('cetrificate_of_origin', 'Certificate of Origin'),
        ('price', 'Price Validity'),
        ('force', 'Force Majeure'),
        ('other', 'Other'),
        ('include', 'Include Section'),
        ('terms_and_conditions', 'Terms & Conditions Sections'),
    ], default='other', required=True)

class OfferingTemplateLines(models.Model):
    _name = "offering.template.line"
    name = fields.Char()
    sequence = fields.Integer(copy=False)
    template_id = fields.Many2one("offering.template")
    offering_id = fields.Many2one("offering.offering")
    template_body = fields.Html(compute="_gen_templates")
    sections = fields.Selection([
        ('intro', 'Intorduction'),
        ('prices', 'Prices'),
        ('shipment', 'Way Of Shipment'),
        ('bank', 'Correspondence Bank'),
        ('software_conditions', 'Special Conditions for Software'),
        ('install','Installation'),
        ('origin_delivery', 'Country of Origin and Delivery Time'),
        ('reserve', 'Reservation of Offer/Performa- Invoice'),
        ('terms', 'Term of Payment'),
        ('warranty', 'Warranty'),
        ('cetrificate_of_origin', 'Certificate of Origin'),
        ('price', 'Price Validity'),
        ('force', 'Force Majeure'),
        ('other', 'Other'),
    ], default="other")

    @api.onchange('sections')
    def _get_section_name(self):
        field_values = {
            'intro': 'Intorduction',
            'prices': 'Prices',
            'shipment': 'Way Of Shipment',
            'bank': 'Correspondence Bank',
            'software_conditions': 'Special Conditions for Software',
            'install':'Installation',
            'origin_delivery': 'Country of Origin and Delivery Time',
            'reserve': 'Reservation of Offer/Performa- Invoice',
            'terms': 'Term of Payment',
            'warranty': 'Warranty',
            'cetrificate_of_origin': 'Certificate of Origin',
            'price': 'Price Validity',
            'force': 'Force Majeure',
            'other': 'Other',
        }
        if self.sections:
            self.name = field_values[self.sections]

    @api.depends('template_id')
    def _gen_templates(self):
        for line in self:
            if not line.template_id:
                line.template_body = "Empty"
                continue
                # raise UserError(_("A report was not selected"))
            if not line.offering_id:
                raise UserError(_("An offering was not selected"))
            res_body = line.template_id.body
            state = []
            while True:
                state.append(res_body)
                field_str = re.search(r"\{([A-Za-z0-9_]+)\}", res_body)
                # group(): string with braces
                # group(1): string without braces
                if field_str:
                    # try:
                        offering_record = line.offering_id.read([field_str.group(1)])[0]
                        fetched_value = offering_record.get(field_str.group(1), False)

                        if fetched_value:
                            # For Relational fields
                            if type(fetched_value) is tuple:
                                field_value = fetched_value[1]
                            # For Date Field
                            elif type(fetched_value) is datetime.date:
                                field_value = fetched_value.strftime("%m/%d/%Y")
                            else:
                                field_value = fetched_value
                            res_body = res_body.replace(field_str.group(), field_value)
                        else:
                            raise UserError(_(f"The called field ({field_str.group(1)}) dones't have a value"))
                else:
                    break
            line.template_body = res_body