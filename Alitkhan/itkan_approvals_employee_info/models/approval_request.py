# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import UserError

class ApprovalRequest(models.Model):
    _inherit="approval.request"

    is_company = fields.Boolean(related="partner_id.is_company")

    employee_name = fields.Char(string="Name", compute='_compute_employee_info')
    job_title = fields.Char(string="Job Title", compute='_compute_employee_info')
    work_email = fields.Char(string="Work Email", compute='_compute_employee_info')
    Work_phone_number = fields.Char(string="Work Phone Number", compute='_compute_employee_info')
    division = fields.Char(string="Division", compute='_compute_employee_info')
    department = fields.Char(string="Department", compute='_compute_employee_info')
    unit = fields.Char(string="Unit", compute='_compute_employee_info')
    direct_manager = fields.Char(string="Direct Manager", compute='_compute_employee_info')
    

    @api.onchange("partner_id")
    def _compute_employee_info(self):
        for record in self:
            user = self.env["res.users"].search([
                ("partner_id", "=", record.partner_id.id)
            ])
            employee = self.env["hr.employee"].search([
                ("user_id", "!=", False),
                ("user_id", "=", user.id),
            ])
            record.employee_name = employee.name if employee else ''
            record.job_title = employee.job_id.name if employee else ''
            record.work_email = employee.work_email if employee else ''
            record.Work_phone_number = employee.work_phone if employee else ''
            record.division = employee.new_divisions.name if employee else ''
            record.department = employee.department_id.name if employee else ''
            record.unit = employee.units if employee else ''
            record.direct_manager = employee.parent_id.name if employee else ''
