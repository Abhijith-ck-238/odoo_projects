from odoo import models, fields


class CustomServiceReportCompany(models.Model):
    _inherit = 'service.report.company'

    sign_of_baneficiary = fields.Text(string="Signature of Baneficiary")
    sign_of_maintenance_administrator = fields.Text(string="Signature of Maintenanace Administrator")
    sign_of_device_operator = fields.Text(string="Signature of Device Operator")
    sign_of_agent = fields.Text(string="Signature of Agent")
