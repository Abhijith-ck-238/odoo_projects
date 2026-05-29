# -*- coding: utf-8 -*-

from odoo import models, fields, api


class ServiceReport(models.Model):
    _name = 'service.report'
    _rec_name="task_number"
    
    task_type = [("job","Job"),("Stand By","Stand By"),("OFF","OFF"),
                ("Note","Note"),("Half Day OFF","Half Day Off"),("Update","Update"),("Remotely","Remotely"),("Instead OFF","Instead OFF"),
                ("Note / Service","Note / Service"),("Others","Others"),("Training","Training")]

    
    task_number = fields.Char(string="Call Number")
    service_number = fields.Char("Service Report Number", readonly=True)
    t_type =fields.Selection(task_type,string="Task Type")
    modality = fields.Many2one("contract.modality",string="Modality")
    travel_from = fields.Many2one("contract.province",string="Travel From")
    travel_to = fields.Many2one("contract.province",string="Travel To")
    
    in_out = fields.Selection([("IN","IN"),("Out","Out")],string="Internal/out")
    date = fields.Date(string="Date of task")
    engineer = fields.Many2one("res.partner",string="Engineer")
    engineer_2 = fields.Many2one("res.partner",string="Engineer 2")
    resource = fields.Text(string="Resource List")
    car = fields.Char(string="Car")
    province = fields.Many2one("contract.province")
    unit = fields.Char(string="Unit")
    type_unit = fields.Char(string="Type")
    sn = fields.Char(string="Serial Number")
    contract = fields.Many2one("contract.contract")
    desc = fields.Html(string="Task Description")
    done_desc = fields.Text(string="Work Done")
    spare = fields.Char(string="Spare Parts Used")
    site = fields.Many2one("contract.site",string="Site")
    state = fields.Char(string="State")
    location = fields.Char(string="Service Report Location")
    task_complete = fields.Selection([("Yes","Yes"),("No","No")],string="Task Complete")
    template_id = fields.Many2one("service.report.company",string="Company Template")
    vehicle_id = fields.Many2one("fleet.vehicle",string="Car")
    old_data = fields.Boolean()

    service_report_time_lines = fields.One2many("service.report.timeline","serv_id")

    hd_name=fields.Char(string="Health dept. name")
    reported_by = fields.Char(string="Call reported By")
    defect = fields.Char(string="Defect")

    contract_line_id = fields.Many2one("contract.product",compute="compute_line_id")

    def print_report(self):
        return self.env.ref("service_reports.action_service_report").report_action([self.id])
# report_action
    def compute_line_id(self):
        for rcd in self:
            contract_line_obj = self.env["contract.product"].search([("contract_id","=",rcd.contract.id),("sn","=",rcd.sn)], order="starting_date desc", limit=1).id
            if not contract_line_obj:
                rcd.contract_line_id = False
            if contract_line_obj:
                rcd.contract_line_id = contract_line_obj
            else:
                rcd.contract_line_id = False
    @api.model
    def create(self, values):
        record = super(ServiceReport, self).create(values)
        record.service_number = "SR-" + str(record.id).zfill(6)
        return record

class ServiceReportTimeLine(models.Model):
    _name="service.report.timeline"

    serv_id = fields.Many2one("service.report")
    date = fields.Date(string="Date")
    time_from =fields.Char(string='From')
    time_to =fields.Char(string='To')
    work = fields.Char(string='Work')
    wait = fields.Char(string='Wait')
    travel = fields.Char(string='Travel')
    total =  fields.Char(string='Total')
    distance = fields.Integer(string="Distance (KM)")

class ServiceReportCom(models.Model):

    _name="service.report.company"
    
    name=fields.Char(string="Name")
    logo = fields.Binary(string="Logo")
    print_company_name = fields.Boolean(string="Print Company Name", default=True)
    kimadia_template = fields.Boolean(string="Kimadia Template", default=True)