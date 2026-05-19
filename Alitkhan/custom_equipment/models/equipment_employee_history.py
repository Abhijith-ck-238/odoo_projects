from odoo import fields, models

class EquipmentEmployeeHistory(models.Model):
    _name = 'equipment.employee.history'
    _description = "Equipment Employee History"
    _inherit = ['mail.thread', 'mail.activity.mixin']

    equipment_id = fields.Many2one('equipment.equipment', string="Equipment")
    acquiring_date = fields.Datetime(string="Acquiring Date")
    employee_id = fields.Many2one('hr.employee', string="Employee")
    return_date = fields.Datetime(string="Return Date")
    attachment_id = fields.Many2many('ir.attachment', string="Handing Attachment")

    @api.model
    def create(self, vals):
        res = super(EquipmentEmployeeHistory, self).create(vals)
        attachment_id = res.mapped('attachment_id')
        attachment_id.write({
            'res_id': res.id,
        })
        return res

    def write(self, vals):
        if vals.get('return_date'):
            old_return_date = self.env['equipment.employee.history'].browse(
                self.id).return_date
            message = 'Employee History - Return Date : ' + str(old_return_date) + " --> " + str(vals.get('return_date'))
            self.equipment_id.message_post(body=message)
        if vals.get('acquiring_date'):
            old_acquiring_date = self.env['equipment.employee.history'].browse(
                self.id).acquiring_date
            message = 'Employee History - Acquiring Date : ' + str(
                old_acquiring_date) + " --> " + str(vals.get('acquiring_date'))
            self.equipment_id.message_post(body=message)
        if vals.get('employee_id'):
            old_employee = self.env['equipment.employee.history'].browse(
                self.id).employee_id.name
            new_employee = self.env['hr.employee'].browse(vals.get('employee_id'))
            message = 'Employee History - Employee Name : ' + str(
                old_employee) + " --> " + str(new_employee.name)
            self.equipment_id.message_post(body=message)
        res = super(EquipmentEmployeeHistory, self).write(vals)
        return res
