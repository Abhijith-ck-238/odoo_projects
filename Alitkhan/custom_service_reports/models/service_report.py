from odoo import models, fields, api


class CustomServiceReport(models.Model):
    _inherit = 'service.report'

    description = fields.Text(string="Reported Defect")
    job_number = fields.Char(string="Job Number")
    note = fields.Text(string="Note")
    hd_name = fields.Char(string="Health dept. name",
                          compute='compute_hd_name', store=True, readonly=False)

    @api.depends('site')
    def compute_hd_name(self):
        for rec in self:
            if rec.site:
                rec.hd_name = rec.site.doh_id.name
            else:
                rec.hd_name = False

    @api.onchange('contract')
    def onchange_contract(self):
        for line in self.contract.product_lines:
            if line.sn == self.sn:
                if line.hd_name.name:
                    self.hd_name = line.hd_name.name
            else:
                pass

    @api.model
    def create(self, values):
        record = super(CustomServiceReport, self).create(values)
        service_report_number = self.env['ir.sequence'].next_by_code(
            'service.report') or 'New'
        # record.service_number = "SR-" + service_report_number
        record.service_number = service_report_number
        return record
