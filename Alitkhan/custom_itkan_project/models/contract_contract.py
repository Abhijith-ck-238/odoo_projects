from odoo import models, fields, api


class ContraContract(models.Model):
    _inherit = "contract.contract"

    itkan_project_id = fields.Many2one("itkan.project", "ALITKAN Project")

    @api.onchange('itkan_project_id')
    def onchange_itkan_project_id(self):
        project = self.env['itkan.project'].browse(self.itkan_project_id.id)
        project.contract_id = self._origin

class ContractProductExtend(models.Model):
    """ Inherited Contract Product"""
    _inherit = 'contract.product'

    x_studio_province = fields.Many2one("contract.province",string="Province",readonly=True)