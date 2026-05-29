from odoo import models, fields, api


class TravellingDetails(models.Model):
    _name = 'travelling.data'

    travel_from = fields.Many2one('contract.province', string="Travel From")
    travel_to = fields.Many2one('contract.province', string="Travel To")
    distance = fields.Integer(string="Distance (KM)")


class CustomServiceReportTimeline(models.Model):
    _inherit = 'service.report.timeline'

    time_from = fields.Char(string='From', default='HH:MM AM/PM')
    time_to = fields.Char(string='To', default='HH:MM AM/PM')

    @api.model
    def write(self, vals):
        service_report_id = self.env['service.report'].browse(self.serv_id.id)
        travelling_data = self.env['travelling.data'].search([('travel_from', '=', service_report_id.travel_from.id),
                                                              ('travel_to', '=', service_report_id.travel_to.id)])
        distance = travelling_data.distance
        vals["distance"] = distance
        res = super(CustomServiceReportTimeline, self).write(vals)
        return res

    @api.model
    def create(self, vals):
        service_report_id = self.env['service.report'].browse(vals["serv_id"])
        travelling_data = self.env['travelling.data'].search([('travel_from', '=', service_report_id.travel_from.id),
                                                              ('travel_to', '=', service_report_id.travel_to.id)])
        distance = travelling_data.distance
        vals["distance"] = distance
        res = super(CustomServiceReportTimeline, self).create(vals)
        return res
