from odoo import fields, models,api


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    equipment_ids = fields.Many2many('equipment.equipment', compute="compute_equipment_ids")


    def compute_equipment_ids(self):
        equipment_line = self.env['equipment.employee.history'].search([('employee_id','=', self.id),
                                                                        ('acquiring_date', '<=', fields.Date.today()),('return_date', '=', False)])
        self.equipment_ids = equipment_line.equipment_id