# -*- coding: utf-8 -*-

from odoo import models, fields, api

class ContractProducts(models.Model):
    _name = "contract.product"
    _parent_name = 'contract_id'

    CONTRACT_TYPES = [("Supplying & Maintenance", "Supplying & Maintenance"),
                      ("Maintenance", "Maintenance"),
                      ("Supplying", "Supplying"),
                      ("3rd party", "3rd party"), ("Demo", "Demo"),
                      ("N.A", "N.A"), ("Other", "Other")]

    name = fields.Char(string="name", compute="_compute_name")
    product_char = fields.Char(string="Product Char")
    product_id = fields.Many2one("product.product", string="Product")
    qty = fields.Integer(string="Quantity")
    price = fields.Float(string="Price",
                         groups="itkan_offering.offering_manager")
    site = fields.Many2one("contract.site", string="Site")
    supplier = fields.Many2one("res.partner", string="Vendor")
    modality = fields.Many2one("contract.modality", string="Modality")
    part_number = fields.Char(string="Part Number")
    sn = fields.Char(string="Serial Number")
    password_validity = fields.Selection([("yes", "Yes"), ("no", "No")],
                                         string="Password/Validity")
    password_validity_date = fields.Date(string="Password Validity Date")
    contract_id = fields.Many2one('contract.contract', readonly=True,
                                  ondelete="cascade")
    functional_location = fields.Char(string="Functional Location", store=True)
    maintainence = fields.Integer(string="Maintainence")
    starting_date = fields.Date(string="Starting Date")
    pac_date = fields.Date(string="PAC Date")
    eoc_date = fields.Date(string="EOC Date", compute='compute_eoc_date')
    warranty = fields.Integer(string="Warranty")
    contract_type = fields.Selection(CONTRACT_TYPES, string="Contract Type")

    def compute_eoc_date(self):
        for item in self:
            start_date = item.starting_date
            warrenty = item.warranty
            if start_date:
                yr = start_date.year
                maintenance = item.maintainence
                yearnew = yr + maintenance + warrenty
                new_date = start_date.replace(year=yearnew)
                item.eoc_date = new_date
            else:
                item.eoc_date = ''

    def _compute_name(self):
        for rcd in self:
            if rcd.product_id:
                rcd.name = rcd.product_id.display_name
            else:
                rcd.name = rcd.product_char or "Empty"

            if rcd.sn:
                rcd.name += ' - ' + rcd.sn

    @api.constrains("site")
    def calc_functional_location(self):
        """ FL = 13 digit = Province number + Digits(Zeros) + Site number """
        for item in self:
            if item.site:
                prov_num = str(item.site.site_province.prov_number)
                site_num = str(item.site.site_number)
                zeros_num = 13 - (int(len(prov_num)) + int(len(site_num)))
                item.functional_location = prov_num + (
                            "0" * zeros_num) + site_num
            else:
                item.functional_location = False
