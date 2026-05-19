# -*- coding: utf-8 -*-

from odoo import models, fields, api

import logging

_logger = logging.getLogger(__name__)

class Contract(models.Model):
    _name = "contract.contract"
    _order = "id desc"
    _inherit = ["mail.thread", "mail.activity.mixin"]

    CONTRACT_CATEG = [("private", "Private"), ("governmental", "Governmental")]

    name = fields.Char(string="Name")
    number = fields.Char()
    iq = fields.Char(string="IQ Number")
    partner_id = fields.Many2one("res.partner", string="Contract With")
    signed_date = fields.Date(string="Signed Date")
    starting_condition = fields.Many2one("contract.condition",
                                         string="Starting Condition")
    notes = fields.Text(string="Notes")
    contract_signed_by = fields.Many2one("res.partner",
                                         string="Contract Signed By")
    first_payment_date = fields.Date(string="First Payment Date")
    project_manager = fields.Many2one("res.partner", string="Project Manager")
    first_payment = fields.Float(string="First Payment",
                                 groups="itkan_offering.offering_manager")
    pm_date = fields.Date(string="PM Date")
    main_contract = fields.Many2one("contract.contract", string="Main Contract")

    contract_categ = fields.Selection(CONTRACT_CATEG,
                                      string="Contract Category")
    attachements = fields.Many2one("ir.attachment", string="Attachments")

    product_lines = fields.One2many('contract.product', "contract_id",
                                    ondelete="cascade")

    province = fields.Many2one("contract.province", string="Province")
    old_data = fields.Boolean()

    sites = fields.Many2many('contract.site', compute="calc_sites")

    """
    Added by AhmedNaseem@29-8-2021
    """
    technical_docs1 = fields.Binary(string="Technical Document 1")
    technical_docs2 = fields.Binary(string="Technical Document 2")

    financial_docs1 = fields.Binary(string="Financial Document 1",
                                    groups="itkan_offering.offering_manager")
    financial_docs2 = fields.Binary(string="Financial Document 2",
                                    groups="itkan_offering.offering_manager")

    """
    Added by AhmedNaseem@11-11-2021

    """

    technical_docs_att = fields.Many2many(comodel_name="ir.attachment",
                                          relation="attachement_contracts_docs_rel",
                                          column1="contract_id",
                                          column2="attachment_id",
                                          string="Technical Documents")

    financial_docs_att = fields.Many2many(comodel_name="ir.attachment",
                                          relation="attachement_contracts_fin_docs_rel",
                                          column1="contract_id",
                                          column2="attachment_id",
                                          string="finanical Documents",
                                          groups="itkan_offering.offering_manager")

    @api.model
    def fix_attachment_res_id(self):
        contracts = self.search([])
        Attachment = self.env['ir.attachment']
        count = 0
        for contract in contracts:
            attachments = (contract.technical_docs_att | contract.financial_docs_att| contract.attachements)

            attachments_to_fix = attachments.filtered(
                lambda att: not att.res_id or att.res_id == 0
            )
            count += len(attachments_to_fix)

            if attachments_to_fix:
                attachments_to_fix.write({
                    'res_id': contract.id,
                    'res_model': contract._name,
                })
            _logger.info("Fixed %s helpdesk attachments", count)
    @api.model
    def create(self, vals):
        res = super(Contract, self).create(vals)
        attachements = res.mapped('attachements')
        technical_docs_att = res.mapped('technical_docs_att')
        financial_docs_att = res.mapped('financial_docs_att')
        dx_financial_documents = res.mapped('dx_financial_documents')
        attachements.write({
            'res_id': res.id,
        })
        technical_docs_att.write({
            'res_id': res.id,
        })
        financial_docs_att.write({
            'res_id': res.id,
        })
        dx_financial_documents.write({
            'res_id': res.id,
        })
        return res

    @api.constrains('iq', 'number')
    def _gen_name(self):
        for contract in self:
            name = ""
            if contract.number:
                name += contract.number
            else:
                if contract.iq:
                    name += contract.iq
                    contract.name = name
                    continue

            name += f" - {contract.iq}"
            contract.name = name

    @api.constrains("product_lines")
    def calc_sites(self):
        sites = []
        for item in self.product_lines:
            sites.append(item.site.id)
        self.sites = sites

    @api.model
    def name_search(self, name='', args=None, operator='ilike', limit=100):
        args = args or []
        domain = ['|', ('name', operator, name), ('iq', operator, name)]
        records = self.search(domain + args, limit=limit)
        return [(rec.id, rec.display_name) for rec in records]
