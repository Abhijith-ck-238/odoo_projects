from odoo import models, fields
from odoo.tools.misc import format_date
import datetime
import calendar


# class CustomHrEmployee(models.Model):
#     _inherit = 'hr.employee'
#
#     check = fields.Boolean(string="cec")

class CustomHrPayslipRun(models.Model):
    _inherit = 'hr.payslip.run'

    def gen_batches(self):
        # generate batches
        currentMonth = datetime.datetime.now().strftime('%B')
        curMonth = datetime.datetime.now().month
        currentYear = datetime.datetime.now().year

        _, num_days = calendar.monthrange(currentYear, curMonth)
        first_day = datetime.date(currentYear, curMonth, 1)
        last_day = datetime.date(currentYear, curMonth, num_days)
        locations = ['Erbil', 'Sulaymaniyah', 'other']

        for loc in range(0, len(locations)):
            if locations[loc] == 'Erbil':
                name = currentMonth + " " + str(currentYear) + " " + "Erbil"
                rec1 = self.env['hr.payslip.run'].search([('name', '=', name)])
                if rec1:
                    pass
                else:
                    self.env['hr.payslip.run'].create({
                        'name': name,
                        'date_start': first_day,
                        'date_end': last_day,
                    })
            elif locations[loc] == 'Sulaymaniyah':
                name = currentMonth + " " + str(
                    currentYear) + " " + "Sulaymaniyah"
                rec1 = self.env['hr.payslip.run'].search([('name', '=', name)])

                if rec1:
                    pass
                else:
                    self.env['hr.payslip.run'].create({
                        'name': name,
                        'date_start': first_day,
                        'date_end': last_day,
                    })
            else:
                name = currentMonth + " " + str(currentYear)
                rec1 = self.env['hr.payslip.run'].search([('name', '=', name)])

                if rec1:
                    pass
                else:
                    self.env['hr.payslip.run'].create({
                        'name': name,
                        'date_start': first_day,
                        'date_end': last_day,
                    })

        # generate payslips
        employees = self.env['hr.employee'].search([])
        for emp in employees:

            if len(emp.contract_ids) == 0:
                pass
            else:

                if emp.work_location_id.name == 'Erbil':
                    name = currentMonth + " " + str(currentYear) + " " + "Erbil"
                    rec1 = self.env['hr.payslip.run'].search([('name', '=', name)])
                    struct_id = emp.contract_id.structure_type_id.default_struct_id
                    payslip_search = self.env['hr.payslip'].search([
                        ('employee_id', '=', emp.id),
                        ('date_from', '=', first_day),
                        ('date_to', '=', last_day)])
                    if payslip_search:
                        pass
                    else:
                        payslip_obj = self.env['hr.payslip'].create({
                            'name': "",
                            'employee_id': emp.id,
                            'struct_id': struct_id.id,
                            'date_from': first_day,
                            'date_to': last_day,
                            'contract_id': emp.contract_id.id,
                            'number': self.env["ir.sequence"].next_by_code(
                                "salary.slip")
                        })
                        payslip_name = payslip_obj.struct_id.payslip_name or 'Salary Slip'
                        payslip_obj.name = '%s - %s - %s' % (
                        payslip_name, payslip_obj.employee_id.name or '',
                        format_date(payslip_obj.env, payslip_obj.date_from, date_format="MMMM y"))

                        if payslip_obj.contract_id:
                            contract_ids = payslip_obj.contract_id.ids
                        contracts = self.env["hr.contract"].browse(contract_ids)
                        payslip_obj.worked_days_line_ids = payslip_obj._get_new_worked_days_lines()
                        rec1.slip_ids = [(4, payslip_obj.id, None)]
                elif emp.work_location_id.name == 'Sulaymaniyah':
                    name = currentMonth + " " + str(currentYear) + " " + "Sulaymaniyah"
                    rec1 = self.env['hr.payslip.run'].search([('name', '=', name)])
                    struct_id = emp.contract_id.structure_type_id.default_struct_id.id
                    payslip_search = self.env['hr.payslip'].search([
                        ('employee_id', '=', emp.id),
                        ('date_from', '=', first_day),
                        ('date_to', '=', last_day)])
                    if payslip_search:
                        pass
                    else:
                        payslip_obj = self.env['hr.payslip'].create({
                            'name': "",
                            'employee_id': emp.id,
                            'struct_id': struct_id,
                            'date_from': first_day,
                            'date_to': last_day,
                            'contract_id': emp.contract_id.id,
                            'number': self.env["ir.sequence"].next_by_code(
                                "salary.slip")

                        })
                        payslip_name = payslip_obj.struct_id.payslip_name or 'Salary Slip'
                        payslip_obj.name = '%s - %s - %s' % (
                            payslip_name, payslip_obj.employee_id.name or '',
                            format_date(payslip_obj.env, payslip_obj.date_from,
                                        date_format="MMMM y"))
                        if payslip_obj.contract_id:
                            contract_ids = payslip_obj.contract_id.ids
                        payslip_obj.worked_days_line_ids = payslip_obj._get_new_worked_days_lines()
                        rec1.slip_ids = [(4, payslip_obj.id,None)]


                else:
                    name = currentMonth + " " + str(currentYear)
                    rec1 = self.env['hr.payslip.run'].search([('name', '=', name)])
                    struct_id = emp.contract_id.structure_type_id.default_struct_id.id
                    payslip_search = self.env['hr.payslip'].search([
                        ('employee_id', '=', emp.id),
                        ('date_from', '=', first_day),
                        ('date_to', '=', last_day)])
                    if payslip_search:
                        pass
                    else:
                        payslip_obj = self.env['hr.payslip'].create({
                            'name': "",
                            'employee_id': emp.id,
                            'struct_id': struct_id,
                            'date_from': first_day,
                            'date_to': last_day,
                            'contract_id': emp.contract_id.id,
                            'number': self.env["ir.sequence"].next_by_code("salary.slip")
                        })
                        payslip_name = payslip_obj.struct_id.payslip_name or 'Salary Slip'
                        payslip_obj.name = '%s - %s - %s' % (
                            payslip_name, payslip_obj.employee_id.name or '',
                            format_date(payslip_obj.env, payslip_obj.date_from,
                                        date_format="MMMM y"))
                        if payslip_obj.contract_id:
                            contract_ids = payslip_obj.contract_id.ids
                        payslip_obj.worked_days_line_ids = payslip_obj._get_new_worked_days_lines()
                        rec1.slip_ids = [(4, payslip_obj.id)]

    def computee_payslips(self):
        return {
            'name': "Compute Sheet",
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'compute.payslip',
            'view_id': self.env.ref(
                'custom_payroll.compute_payslip_wizard_view').id,
            'target': 'new',
        }
