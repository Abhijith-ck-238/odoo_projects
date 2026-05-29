from odoo import models, api


class CustomApprovalRequest(models.Model):
    _inherit = "approval.request"

    # @api.onchange("partner_id")
    # def _compute_employee_info(self):
    #     print("ssssssssssssssssssssssssssssssss")
    #     for record in self:
    #         user = self.env["res.users"].search([
    #             ("partner_id", "=", record.partner_id.id)
    #         ])
    #         employee = self.env["hr.employee"].search([
    #             ("user_id", "!=", False),
    #             ("user_id", "=", user.id),
    #         ])
    #         print("emoooooooooooooooooooo",employee)
    #         record.employee_name = employee.name if employee else ''
    #         record.job_title = employee.job_id.name
    #         record.work_email = employee.work_email
    #         record.Work_phone_number = employee.work_phone
    #         record.division = employee.new_divisions.name
    #         record.department = employee.department_id.name
    #         record.unit = employee.new_units.name
    #         record.direct_manager = employee.parent_id.name
