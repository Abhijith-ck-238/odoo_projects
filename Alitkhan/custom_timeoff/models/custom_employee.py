from odoo import models, fields


class CustomEmployee(models.Model):
    _inherit = 'hr.employee'

    current_leave_state = fields.Selection(selection_add=[('time_off_officer', 'Time off Officer Approval'),
                                                          ('time_off_responsible', 'Time off Responsible Approval')])
    notified_user_ids = fields.Many2many('res.users',
                                         string='Users Notified')
class CustomEmployeePublic(models.Model):
    _inherit = 'hr.employee.public'

    notified_user_ids = fields.Many2many('res.users',
                                         string='Users Notified')

class CustomEmployeeBase(models.AbstractModel):
    _inherit = 'hr.employee.base'

    current_leave_state = fields.Selection(selection_add=[('time_off_officer', 'Time off Officer Approval'),
                                                          ('time_off_responsible', 'Time off Responsible Approval')])
    notified_user_ids = fields.Many2many('res.users',
                                         string='Users Notified', relation="emp_bse_user_rel", column1="emp_id", column2="user_id")
