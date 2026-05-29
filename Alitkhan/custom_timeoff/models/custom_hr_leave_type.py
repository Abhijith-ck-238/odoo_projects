from odoo import models, fields


class CustomHrLeaveType(models.Model):
    _inherit = 'hr.leave.type'
    _description = 'Leave Type'

    notify_department_manager_after = fields.Integer(
        string="Notify Department Manager After")
    leave_validation_type = fields.Selection(
        selection_add=[('direct_manager', 'Direct Manager'),
                       ('direct_manager_and_time_off_officer',
                        'Direct Manager and Time off officer'),
                       ('time_off_responsible', 'Time Off Responsible'),
                       ('time_off_responsible_and_time_off_officer',
                        'Time Off Responsible and Time off Officer'),
                       ('direct_manager_and_second_direct_manager',
                        'Direct Manager And Second Direct Manager'),
                       ('direct_and_second_direct_and_time_off_officer',
                        'Direct Manager,Second Direct Manager and Time Off Officer')
                       ])

    # def get_days(self, employee_id):
    #     return self.get_employees_days([employee_id])[employee_id]
    #
    # def get_employees_days(self, employee_ids):
    #     result = {
    #         employee_id: {
    #             leave_type.id: {
    #                 'max_leaves': 0,
    #                 'leaves_taken': 0,
    #                 'remaining_leaves': 0,
    #                 'virtual_remaining_leaves': 0,
    #             } for leave_type in self
    #         } for employee_id in employee_ids
    #     }
    #     start_date = fields.Datetime.now().date().replace(month=1, day=1)
    #     end_date = fields.Datetime.now().date().replace(month=12, day=31)
    #     requests = self.env['hr.leave'].search([
    #         ('employee_id', 'in', employee_ids),
    #         ('state', 'in', ['confirm', 'validate1', 'validate']),
    #         ('holiday_status_id', 'in', self.ids),
    #         ('date_from', '>=', start_date), ('date_to', '<=', end_date),
    #
    #     ])
    #     allocations = self.env['hr.leave.allocation'].sudo().search([
    #         ('employee_id', 'in', employee_ids),
    #         ('state', 'in', ['confirm', 'validate1', 'validate']),
    #         ('holiday_status_id', 'in', self.ids),
    #         ('create_date', '>=', start_date), ('create_date', '<=', end_date)
    #     ])
    #     for request in requests:
    #
    #         status_dict = result[request.employee_id.id][
    #             request.holiday_status_id.id]
    #         status_dict['virtual_remaining_leaves'] -= (
    #             request.number_of_hours_display
    #             if request.leave_type_request_unit == 'hour'
    #             else request.number_of_days)
    #         if request.state == 'validate':
    #             status_dict['leaves_taken'] += (request.number_of_hours_display
    #                                             if request.leave_type_request_unit == 'hour'
    #                                             else request.number_of_days)
    #             status_dict['remaining_leaves'] -= (
    #                 request.number_of_hours_display
    #                 if request.leave_type_request_unit == 'hour'
    #                 else request.number_of_days)
    #
    #     for allocation in allocations.sudo():
    #         status_dict = result[allocation.employee_id.id][
    #             allocation.holiday_status_id.id]
    #         if allocation.state == 'validate':
    #             # note: add only validated allocation even for the virtual
    #             # count; otherwise pending then refused allocation allow
    #             # the employee to create more leaves than possible
    #             status_dict['virtual_remaining_leaves'] += (
    #                 allocation.number_of_hours_display
    #                 if allocation.type_request_unit == 'hour'
    #                 else allocation.number_of_days)
    #             status_dict['max_leaves'] += (allocation.number_of_hours_display
    #                                           if allocation.type_request_unit == 'hour'
    #                                           else allocation.number_of_days)
    #             status_dict['remaining_leaves'] += (
    #                 allocation.number_of_hours_display
    #                 if allocation.type_request_unit == 'hour'
    #                 else allocation.number_of_days)
    #     return result
