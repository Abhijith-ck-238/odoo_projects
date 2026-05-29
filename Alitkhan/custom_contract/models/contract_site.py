from odoo import models, fields


class CustomContractSite(models.Model):
    _inherit = 'contract.site'

    doh_id = fields.Many2one('health.department', string="DOH")
    site_number = fields.Integer(string="Site Number", default=lambda self: self._last_site_number())

    def _last_site_number(self):
        last_site_number = self.env['contract.site'].search([]).mapped(
            'site_number')
        return (max(last_site_number) if last_site_number else 0) + 1

    def merge_sites(self):
        helpdesk_ticket_ids = self.env['helpdesk.ticket'].search(
            [('site_id', 'in', self.ids)])
        fs_ticket_ids = self.env['project.task'].search(
            [('site_id', 'in', self.ids)])
        pm_ids = self.env['preventive.maintainence'].search(
            [('site', 'in', self.ids)])
        service_report_ids = self.env['service.report'].search(
            [('site', 'in', self.ids)])
        contract_product_ids = self.env['contract.product'].search(
            [('site', 'in', self.ids)])
        i = 0
        for site in self:
            if i == 0:
                pass
            else:
                if site.site_province:
                    if self[0].site_province:
                        pass
                    else:
                        self[0].site_province = site.site_province.id
                if site.site_number:
                    if self[0].site_number:
                        pass
                    else:
                        self[0].site_number = site.site_number
                for helpdesk_ticket in helpdesk_ticket_ids:
                    helpdesk_ticket.site_id = self[0].id
                for fs_ticket in fs_ticket_ids:
                    fs_ticket.site_id = self[0].id
                for fs_ticket in fs_ticket_ids:
                    fs_ticket.site_id = self[0].id
                for pm_id in pm_ids:
                    pm_id.site = self[0].id
                for service_report in service_report_ids:
                    service_report.site = self[0].id
                for contract_product in contract_product_ids:
                    contract_product.site = self[0].id
                site.unlink()
            i = i + 1
