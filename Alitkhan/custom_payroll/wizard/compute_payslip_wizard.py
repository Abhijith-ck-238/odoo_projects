from odoo import models, fields, api


class CustomHrEmployees(models.Model):
    _inherit = 'hr.employee'

    batch_id = fields.Many2one('compute.payslip', string="Batch")


class CustomPublicEmployeeInherit(models.Model):
    _inherit = 'hr.employee.public'

    batch_id = fields.Many2one('compute.payslip', string="Batch")

class ComputePayslip(models.Model):
    _name = "compute.payslip"
    _description = 'Compute Payslip for all employees'

    batches = fields.Many2one('hr.payslip.run',
                               string="Batches"
                               )
    employee_ids = fields.Many2many('hr.employee', 'hr_employee_rel', 'batch_id', 'emp_id', string="Employees",
                                    required=True)

    @api.onchange("batches")
    def onchange_employee_ids(self):
        for rec in self:
            # lines = [(5, 0, 0)]
            vals = []
            for emp in rec.batches:
                for line in emp.slip_ids:
                    if line.state == 'done' or line.state == 'verify' or line.state == 'cancel':
                        pass
                    else:
                        vals.append(line.employee_id.id)
            rec.employee_ids = vals

    def compute_sheet(self):
        for emp in self.employee_ids:
            for slip in emp.slip_ids:
                if slip.date_from == self.batches.date_start and slip.date_to == self.batches.date_end and slip.state == 'draft':
                    slip.compute_sheet()
                else:
                    pass



