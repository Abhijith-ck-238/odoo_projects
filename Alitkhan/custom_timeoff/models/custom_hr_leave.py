from odoo import models, fields, api, _, SUPERUSER_ID
from odoo.exceptions import ValidationError, UserError
from pytz import timezone, UTC
from odoo.addons.hr_holidays.models.hr_leave import HolidaysRequest

from datetime import datetime


# class HolidaysRequestMpatch(HolidaysRequest):
#
#     def _read(self, fields):
#         fields = set(fields)
#         if 'name' in fields and 'employee_id' not in fields:
#             fields.add('employee_id')
#         super(HolidaysRequest, self)._read(fields)
#
#     HolidaysRequest._read = _read


class CustomHrLeave(models.Model):
    _inherit = 'hr.leave'
    _description = 'Hr Leave'

    holiday_status_id = fields.Many2one(
        "hr.leave.type", compute='_compute_from_employee_id',
        store=True, string="Time Off Type",
        required=True, readonly=False,
        domain="""[
                ('company_id', 'in', [employee_company_id, False]),
                '|',
                    ('requires_allocation', '=', 'no'),
                    ('has_valid_allocation', '=', True),
            ]""",
        tracking=True)

    # user_notified = fields.Many2many('res.users', string="Users Notified", store=True, readonly=True)
    user_notified = fields.Many2many(
        'res.users',
        string="Users Notified",
        store=True,
        readonly=True,
        compute='_compute_user_notified'
    )

    state = fields.Selection(
        selection_add=[('time_off_officer', 'Time off Officer Approval'),
                       ('time_off_responsible',
                        'Time off Responsible Approval')])
    agenda_id = fields.Many2one('agenda.agenda', string="Agenda")
    new_divisions = fields.Many2one('division.division', related="employee_id.new_divisions")
    new_units = fields.Many2one('unit.unit', related='employee_id.new_units')

    def write(self, values):
        is_officer = self.env.user.has_group('hr_holidays.group_hr_holidays_user') or self.env.is_superuser()
        is_time_off_officer = self.env.user.has_group(
            'custom_timeoff.group_hr_officer')
        if not is_officer and not is_time_off_officer and values.keys() - {'attachment_ids', 'supported_attachment_ids', 'message_main_attachment_id'}:
            if any(hol.date_from.date() < fields.Date.today() and hol.employee_id.leave_manager_id != self.env.user
                   and hol.state not in ('confirm', 'draft') for hol in self):
                raise UserError(_('You must have manager rights to modify/validate a time off that already begun'))
            if any(leave.state == 'cancel' for leave in self):
                raise UserError(_('Only a manager can modify a canceled leave.'))

        # Unlink existing resource.calendar.leaves for validated time off
        if 'state' in values and values['state'] != 'validate':
            validated_leaves = self.filtered(lambda l: l.state == 'validate')
            validated_leaves._remove_resource_leave()

        employee_id = values.get('employee_id', False)
        if not self.env.context.get('leave_fast_create'):
            if values.get('state'):
                self._check_approval_update(values['state'])
                if any(holiday.validation_type == 'both' for holiday in self):
                    if values.get('employee_id'):
                        employees = self.env['hr.employee'].browse(values.get('employee_id'))
                    else:
                        employees = self.mapped('employee_id')
                    self._check_double_validation_rules(employees, values['state'])
            if 'date_from' in values:
                values['request_date_from'] = values['date_from']
            if 'date_to' in values:
                values['request_date_to'] = values['date_to']
        result = super(HolidaysRequest, self).write(values)
        if any(field in values for field in ['request_date_from', 'date_from', 'request_date_from', 'date_to', 'holiday_status_id', 'employee_id', 'state']):
            self.sudo()._check_validity()
        if not self.env.context.get('leave_fast_create'):
            for holiday in self:
                if employee_id:
                    holiday.add_follower(employee_id)

        return result

    # def _check_approval_update(self, state):
    #     """ Check if target state is achievable. """
    #     if self.env.is_superuser():
    #         return
    #
    #     current_employee = self.env.user.employee_id
    #     is_officer = self.env.user.has_group('hr_holidays.group_hr_holidays_user')
    #     is_manager = self.env.user.has_group('hr_holidays.group_hr_holidays_manager')
    #
    #     for holiday in self:
    #         val_type = holiday.validation_type
    #
    #         if not is_manager:
    #             if holiday.state == 'cancel' and state != 'confirm':
    #                 raise UserError(_('A cancelled leave cannot be modified.'))
    #             if state == 'confirm':
    #                 if holiday.state == 'refuse':
    #                     raise UserError(_('Only a Time Off Manager can reset a refused leave.'))
    #                 if holiday.date_from and holiday.date_from.date() <= fields.Date.today():
    #                     raise UserError(_('Only a Time Off Manager can reset a started leave.'))
    #                 if holiday.employee_id != current_employee:
    #                     raise UserError(_('Only a Time Off Manager can reset other people leaves.'))
    #             else:
    #                 if val_type == 'no_validation' and current_employee == holiday.employee_id and (is_officer or is_manager):
    #                     continue
    #                 # use ir.rule based first access check: department, members, ... (see security.xml)
    #                 holiday.check_access('write')
    #
    #                 # This handles states validate1 validate and refuse
    #                 if holiday.employee_id == current_employee\
    #                         and self.env.user != holiday.employee_id.leave_manager_id\
    #                         and not is_officer:
    #                     raise UserError(_('Only a Time Off Officer or Manager can approve/refuse its own requests.'))
    #
    #                 if (state == 'validate1' and val_type == 'both'):
    #                     if not is_officer and self.env.user != holiday.employee_id.leave_manager_id:
    #                         raise UserError(_('You must be either %s\'s manager or Time off Manager to approve this leave') % (holiday.employee_id.name))
    #
    #                 if (state == 'validate' and val_type == 'manager')\
    #                         and self.env.user != holiday.employee_id.leave_manager_id\
    #                         and not is_officer:
    #                     raise UserError(_("You must be %s's Manager to approve this leave", holiday.employee_id.name))
    #
    #                 if not is_officer and (state == 'validate' and val_type == 'hr'):
    #                     raise UserError(_('You must either be a Time off Officer or Time off Manager to approve this leave'))

    def _check_approval_update(self, state):
        """ Check if target state is achievable. """
        if self.env.is_superuser():
            return

        current_employee = self.env.user.employee_id
        is_officer = self.env.user.has_group(
            'hr_holidays.group_hr_holidays_user')
        is_manager = self.env.user.has_group(
            'hr_holidays.group_hr_holidays_manager')

        for holiday in self:
            val_type = holiday.validation_type

            if not is_manager and state != 'confirm':
                if state == 'draft':
                    if holiday.state == 'refuse':
                        raise UserError(
                            _('Only a Leave Manager can reset a refused leave.'))
                    if holiday.date_from and holiday.date_from.date() <= fields.Date.today():
                        raise UserError(
                            _('Only a Leave Manager can reset a started leave.'))
                    if holiday.employee_id != current_employee:
                        raise UserError(
                            _('Only a Leave Manager can reset other people '
                              'leaves.'))
                else:
                    if val_type == 'no_validation' and current_employee == holiday.employee_id:
                        continue
                    # use ir.rule based first access check: department,
                    # members, ... (see security.xml)
                    holiday.check_access_rule('write')

                    # This handles states validate1 validate and refuse
                    # if holiday.holiday_status_id.validation_type != 'direct_director' and holiday.employee_id == current_employee:
                    #     raise UserError(_('Only a Leave Manager can approve/refuse its own requests.'))

                    if (state == 'validate1' and val_type == 'both') or (
                            state == 'validate' and val_type == 'manager') and holiday.holiday_type == 'employee':
                        if not is_officer and self.env.user != holiday.employee_id.leave_manager_id:
                            raise UserError(
                                _('You must be either %s\'s manager or Leave manager to approve this leave') % (
                                    holiday.employee_id.name))

    @api.depends('employee_id')
    def _compute_from_employee_id(self):
        for holiday in self:
            holiday.manager_id = holiday.employee_id.parent_id.id if holiday.employee_id else False

            # Only continue if employee is set
            if not holiday.employee_id:
                holiday.holiday_status_id = False
                continue

            # Try finding a matching holiday type
            leave_type = self.env['hr.leave.type'].search([
                ('company_id', 'in',
                 [holiday.employee_id.company_id.id, False]),
                '|',
                ('requires_allocation', '=', 'no'),
                ('has_valid_allocation', '=', True),
            ], limit=1)

            # Assign if current user is allowed
            if holiday.employee_id.user_id == self.env.user or holiday._origin.employee_id == holiday.employee_id:
                holiday.holiday_status_id = leave_type
            else:
                # Additional validation for allocation
                if leave_type:
                    holiday.holiday_status_id = leave_type
                else:
                    holiday.holiday_status_id = False

    # @api.depends('employee_id')
    # def _compute_from_employee_id(self):
    #     for holiday in self:
    #         holiday.manager_id = holiday.employee_id.parent_id.id
    #         if holiday.holiday_status_id.requires_allocation == 'no':
    #             continue
    #         if not holiday.employee_id:
    #             holiday.holiday_status_id = False
    #         elif holiday.employee_id.user_id != self.env.user and holiday._origin.employee_id != holiday.employee_id:
    #             if holiday.employee_id and not holiday.holiday_status_id.with_context(
    #                     employee_id=holiday.employee_id.id).has_valid_allocation:
    #                 holiday.holiday_status_id = False

    # @api.onchange('holiday_status_id')
    # def _onchange_holiday_status_id(self):
    #     for rec in self:
    #         user_ids = []
    #
    #         validation_type = rec.holiday_status_id.leave_validation_type
    #
    #         if validation_type == 'no_validation':
    #             return
    #
    #         if validation_type == 'hr':
    #             if rec.holiday_status_id.responsible_ids:
    #                 user_ids += rec.holiday_status_id.responsible_ids.ids
    #             else:
    #                 return {
    #                     'warning': {
    #                         'title': _('Missing Responsible'),
    #                         'message': _(
    #                             'No Responsible person set on Time off Type.')
    #                     }
    #                 }
    #
    #         elif validation_type == 'manager':
    #             if rec.employee_id.parent_id.user_id:
    #                 user_ids.append(rec.employee_id.parent_id.user_id.id)
    #             else:
    #                 return {
    #                     'warning': {
    #                         'title': _('Missing Manager'),
    #                         'message': _('Employee has no Manager.')
    #                     }
    #                 }
    #
    #         elif validation_type == 'both':
    #             if rec.employee_id.parent_id.user_id:
    #                 user_ids.append(rec.employee_id.parent_id.user_id.id)
    #             if rec.holiday_status_id.responsible_ids:
    #                 user_ids += rec.holiday_status_id.responsible_ids.ids
    #             if not user_ids:
    #                 return {
    #                     'warning': {
    #                         'title': _('Missing Approvers'),
    #                         'message': _(
    #                             'Please set a Manager for Employee and a Responsible person on Time Off Type.')
    #                     }
    #                 }
    #
    #         elif validation_type == 'direct_manager':
    #             if rec.employee_id.direct_manager_id:
    #                 user_ids.append(rec.employee_id.direct_manager_id.id)
    #             else:
    #                 return {
    #                     'warning': {
    #                         'title': _('Missing Direct Manager'),
    #                         'message': _('Employee has no Direct Manager.')
    #                     }
    #                 }
    #
    #         elif validation_type == 'direct_manager_and_time_off_officer':
    #             if rec.employee_id.direct_manager_id:
    #                 user_ids.append(rec.employee_id.direct_manager_id.id)
    #             if rec.holiday_status_id.responsible_ids:
    #                 user_ids += rec.holiday_status_id.responsible_ids.ids
    #             if not user_ids:
    #                 return {
    #                     'warning': {
    #                         'title': _('Missing Approvers'),
    #                         'message': _(
    #                             'Employee has no Direct Manager and Time Off Officer.')
    #                     }
    #                 }
    #
    #         elif validation_type == 'time_off_responsible':
    #             if rec.employee_id.leave_manager_id:
    #                 user_ids.append(rec.employee_id.leave_manager_id.id)
    #             else:
    #                 return {
    #                     'warning': {
    #                         'title': _('Missing Time Off Responsible'),
    #                         'message': _(
    #                             'Employee has no Time Off Responsible.')
    #                     }
    #                 }
    #
    #         elif validation_type == 'time_off_responsible_and_time_off_officer':
    #             if rec.employee_id.leave_manager_id:
    #                 user_ids.append(rec.employee_id.leave_manager_id.id)
    #             if rec.holiday_status_id.responsible_ids:
    #                 user_ids += rec.holiday_status_id.responsible_ids.ids
    #             if not user_ids:
    #                 return {
    #                     'warning': {
    #                         'title': _('Missing Approvers'),
    #                         'message': _(
    #                             'Employee has no Time Off Officer and Time Off Responsible.')
    #                     }
    #                 }
    #
    #         elif validation_type == 'direct_manager_and_second_direct_manager':
    #             if rec.employee_id.direct_manager_id:
    #                 user_ids.append(rec.employee_id.direct_manager_id.id)
    #             if rec.employee_id.second_direct_manager_id:
    #                 user_ids.append(rec.employee_id.second_direct_manager_id.id)
    #             if not user_ids:
    #                 return {
    #                     'warning': {
    #                         'title': _('Missing Managers'),
    #                         'message': _(
    #                             'Employee has no Direct or Second Direct Manager.')
    #                     }
    #                 }
    #
    #         elif validation_type == 'direct_and_second_direct_and_time_off_officer':
    #             if rec.employee_id.direct_manager_id:
    #                 user_ids.append(rec.employee_id.direct_manager_id.id)
    #             if rec.employee_id.second_direct_manager_id:
    #                 user_ids.append(rec.employee_id.second_direct_manager_id.id)
    #             if rec.holiday_status_id.responsible_ids:
    #                 user_ids += rec.holiday_status_id.responsible_ids.ids
    #             if not user_ids:
    #                 return {
    #                     'warning': {
    #                         'title': _('Missing All Approvers'),
    #                         'message': _(
    #                             'Employee has no Direct Manager, Second Direct Manager, or Time Off Officer.')
    #                     }
    #                 }
    #
    #         rec.user_notified = [(6, 0, user_ids)] if user_ids else False

    @api.depends('holiday_status_id', 'employee_id.parent_id.user_id',
                 'employee_id.direct_manager_id',
                 'employee_id.second_direct_manager_id',
                 'employee_id.leave_manager_id',
                 'holiday_status_id.responsible_ids')

    def _compute_user_notified(self):
        for rec in self:
            user_ids = []
            validation_type = rec.holiday_status_id.leave_validation_type

            if not validation_type:
                rec.user_notified = False
                continue

            if validation_type == 'hr':
                user_ids = rec.holiday_status_id.responsible_ids.ids or []

            elif validation_type == 'manager':
                if rec.employee_id.parent_id.user_id:
                    user_ids = [rec.employee_id.parent_id.user_id.id]

            elif validation_type == 'both':
                if rec.employee_id.parent_id.user_id:
                    user_ids.append(rec.employee_id.parent_id.user_id.id)
                if rec.holiday_status_id.responsible_ids:
                    user_ids += rec.holiday_status_id.responsible_ids.ids

            elif validation_type == 'direct_manager':
                if rec.employee_id.direct_manager_id:
                    user_ids = [rec.employee_id.direct_manager_id.id]

            elif validation_type == 'direct_manager_and_time_off_officer':
                if rec.employee_id.direct_manager_id:
                    user_ids.append(rec.employee_id.direct_manager_id.id)
                if rec.holiday_status_id.responsible_ids:
                    user_ids += rec.holiday_status_id.responsible_ids.ids

            elif validation_type == 'time_off_responsible':
                if rec.employee_id.leave_manager_id:
                    user_ids = [rec.employee_id.leave_manager_id.id]

            elif validation_type == 'time_off_responsible_and_time_off_officer':
                if rec.employee_id.leave_manager_id:
                    user_ids.append(rec.employee_id.leave_manager_id.id)
                if rec.holiday_status_id.responsible_ids:
                    user_ids += rec.holiday_status_id.responsible_ids.ids

            elif validation_type == 'direct_manager_and_second_direct_manager':
                if rec.employee_id.direct_manager_id:
                    user_ids.append(rec.employee_id.direct_manager_id.id)
                if rec.employee_id.second_direct_manager_id:
                    user_ids.append(rec.employee_id.second_direct_manager_id.id)

            elif validation_type == 'direct_and_second_direct_and_time_off_officer':
                if rec.employee_id.direct_manager_id:
                    user_ids.append(rec.employee_id.direct_manager_id.id)
                if rec.employee_id.second_direct_manager_id:
                    user_ids.append(rec.employee_id.second_direct_manager_id.id)
                if rec.holiday_status_id.responsible_ids:
                    user_ids += rec.holiday_status_id.responsible_ids.ids

            rec.user_notified = [(6, 0, user_ids)] if user_ids else False

    # @api.model
    # def create(self, vals):
    #     print(vals,'vals_list....')
    #     record = super().create(vals)
    #     time_off_type_id = vals['holiday_status_id']
    #
    #     date_from = datetime.strptime(vals['request_date_from'], '%Y-%m-%d')
    #     date_to = datetime.strptime(vals['request_date_to'], '%Y-%m-%d')
    #     duration = (date_to - date_from).days + 1  # inclusive of both days
    #     number_of_days = duration
    #     time_off_type_obj = self.env['hr.leave.type'].browse(time_off_type_id)
    #     employee_id = vals['employee_id']
    #     emp_obj = self.env['hr.employee'].browse(employee_id)
    #     leave_limit = time_off_type_obj.notify_department_manager_after
    #     validation_type = time_off_type_obj.leave_validation_type
    #
    #     if validation_type == 'no_validation':
    #         res = super(CustomHrLeave, self).create(vals)
    #         leave_sudo = res.sudo()
    #         partners = []
    #         if leave_sudo.employee_id.direct_manager_id.partner_id.id:
    #             partners.append(
    #                 leave_sudo.employee_id.direct_manager_id.partner_id.id)
    #         if leave_sudo.employee_id.second_direct_manager_id.partner_id.id:
    #             partners.append(
    #                 leave_sudo.employee_id.second_direct_manager_id.partner_id.id)
    #         if leave_sudo.employee_id.director_id.partner_id.id:
    #             partners.append(
    #                 leave_sudo.employee_id.director_id.partner_id.id)
    #         if leave_sudo.employee_id.parent_id.user_id.partner_id.id:
    #             partners.append(
    #                 leave_sudo.employee_id.parent_id.user_id.partner_id.id)
    #         if leave_sudo.employee_id.leave_manager_id.partner_id.id:
    #             partners.append(
    #                 leave_sudo.employee_id.leave_manager_id.partner_id.id)
    #         leave_sudo.message_subscribe(partner_ids=partners)
    #         if leave_sudo.employee_id and leave_sudo.holiday_status_id and leave_sudo.holiday_status_id.validation_type == 'direct_director':
    #             leave_sudo.send_for_approval()
    #         return res
    #     elif validation_type == 'direct_manager':
    #         if leave_limit == 0 or number_of_days <= leave_limit:
    #             res = super(CustomHrLeave, self).create(vals)
    #             leave_sudo = res.sudo()
    #             partners = []
    #             if leave_sudo.employee_id.direct_manager_id.partner_id.id:
    #                 partners.append(
    #                     leave_sudo.employee_id.direct_manager_id.partner_id.id)
    #             if leave_sudo.employee_id.second_direct_manager_id.partner_id.id:
    #                 partners.append(
    #                     leave_sudo.employee_id.second_direct_manager_id.partner_id.id)
    #             if leave_sudo.employee_id.director_id.partner_id.id:
    #                 partners.append(
    #                     leave_sudo.employee_id.director_id.partner_id.id)
    #             if leave_sudo.employee_id.parent_id.user_id.partner_id.id:
    #                 partners.append(
    #                     leave_sudo.employee_id.parent_id.user_id.partner_id.id)
    #             if leave_sudo.employee_id.leave_manager_id.partner_id.id:
    #                 partners.append(
    #                     leave_sudo.employee_id.leave_manager_id.partner_id.id)
    #             leave_sudo.message_subscribe(partner_ids=partners)
    #             if leave_sudo.employee_id and leave_sudo.holiday_status_id and leave_sudo.holiday_status_id.validation_type == 'direct_director':
    #                 leave_sudo.send_for_approval()
    #             return res
    #
    #         else:
    #             res = super(CustomHrLeave, self).create(vals)
    #             leave_sudo = res.sudo()
    #             partners = []
    #             if leave_sudo.employee_id.direct_manager_id.partner_id.id:
    #                 partners.append(
    #                     leave_sudo.employee_id.direct_manager_id.partner_id.id)
    #             if leave_sudo.employee_id.second_direct_manager_id.partner_id.id:
    #                 partners.append(
    #                     leave_sudo.employee_id.second_direct_manager_id.partner_id.id)
    #             if leave_sudo.employee_id.director_id.partner_id.id:
    #                 partners.append(
    #                     leave_sudo.employee_id.director_id.partner_id.id)
    #             if leave_sudo.employee_id.parent_id.user_id.partner_id.id:
    #                 partners.append(
    #                     leave_sudo.employee_id.parent_id.user_id.partner_id.id)
    #             if leave_sudo.employee_id.leave_manager_id.partner_id.id:
    #                 partners.append(
    #                     leave_sudo.employee_id.leave_manager_id.partner_id.id)
    #             leave_sudo.message_subscribe(partner_ids=partners)
    #             if leave_sudo.employee_id and leave_sudo.holiday_status_id and leave_sudo.holiday_status_id.validation_type == 'direct_director':
    #                 leave_sudo.send_for_approval()
    #             if emp_obj.new_divisions.name == 'Technical':
    #                 channel_id = self.env.ref(
    #                     'custom_timeoff.technical_time_off_notifications')
    #                 user_id = emp_obj.user_id.partner_id.id
    #                 direct_manager_id = emp_obj.direct_manager_id.partner_id
    #                 notification_ids = [((0, 0, {
    #                     'res_partner_id': direct_manager_id.id,
    #                     'notification_type': 'inbox'}))]
    #                 message = _(
    #                     "%s has requested %d days on the time off request <a href=# data-oe-model=hr.leave "
    #                     "data-oe-id=%d>%s</a>.") % (
    #                               emp_obj.name,
    #                               res.number_of_days,
    #                               res.id,
    #                               res.name)
    #                 channel_id.message_post(author_id=user_id,
    #                                         body=_(message),
    #                                         message_type='notification',
    #                                         subtype='mail.mt_comment',
    #                                         notification_ids=notification_ids,
    #                                         partner_ids=[direct_manager_id.id],
    #                                         )
    #
    #             else:
    #                 channel_id = self.env.ref(
    #                     'custom_timeoff.general_time_off_notifications')
    #                 user_id = emp_obj.user_id.partner_id.id
    #                 direct_manager_id = emp_obj.direct_manager_id.partner_id
    #                 notification_ids = [((0, 0, {
    #                     'res_partner_id': direct_manager_id.id,
    #                     'notification_type': 'inbox'}))]
    #                 message = _(
    #                     "%s has requested %d days on the time off request <a href=# data-oe-model=hr.leave "
    #                     "data-oe-id=%d>%s</a>.") % (
    #                               emp_obj.name,
    #                               res.number_of_days,
    #                               res.id,
    #                               res.name)
    #             channel_id.message_post(author_id=user_id,
    #                                     body=_(message),
    #                                     message_type='notification',
    #                                     subtype='mail.mt_comment',
    #                                     notification_ids=notification_ids,
    #                                     partner_ids=[direct_manager_id.id],
    #                                     )
    #             return res
    #
    #     elif validation_type == 'direct_manager_and_time_off_officer':
    #         if leave_limit == 0 or number_of_days <= leave_limit:
    #             res = super(CustomHrLeave, self).create(vals)
    #             leave_sudo = res.sudo()
    #             partners = []
    #             if leave_sudo.employee_id.direct_manager_id.partner_id.id:
    #                 partners.append(
    #                     leave_sudo.employee_id.direct_manager_id.partner_id.id)
    #             if leave_sudo.employee_id.second_direct_manager_id.partner_id.id:
    #                 partners.append(
    #                     leave_sudo.employee_id.second_direct_manager_id.partner_id.id)
    #             if leave_sudo.employee_id.director_id.partner_id.id:
    #                 partners.append(
    #                     leave_sudo.employee_id.director_id.partner_id.id)
    #             if leave_sudo.employee_id.parent_id.user_id.partner_id.id:
    #                 partners.append(
    #                     leave_sudo.employee_id.parent_id.user_id.partner_id.id)
    #             if leave_sudo.employee_id.leave_manager_id.partner_id.id:
    #                 partners.append(
    #                     leave_sudo.employee_id.leave_manager_id.partner_id.id)
    #             leave_sudo.message_subscribe(partner_ids=partners)
    #             if leave_sudo.employee_id and leave_sudo.holiday_status_id and leave_sudo.holiday_status_id.validation_type == 'direct_director':
    #                 leave_sudo.send_for_approval()
    #             res.state = 'direct_manager'
    #             return res
    #
    #         else:
    #             res = super(CustomHrLeave, self).create(vals)
    #             leave_sudo = res.sudo()
    #             partners = []
    #             if leave_sudo.employee_id.direct_manager_id.partner_id.id:
    #                 partners.append(
    #                     leave_sudo.employee_id.direct_manager_id.partner_id.id)
    #             if leave_sudo.employee_id.second_direct_manager_id.partner_id.id:
    #                 partners.append(
    #                     leave_sudo.employee_id.second_direct_manager_id.partner_id.id)
    #             if leave_sudo.employee_id.director_id.partner_id.id:
    #                 partners.append(
    #                     leave_sudo.employee_id.director_id.partner_id.id)
    #             if leave_sudo.employee_id.parent_id.user_id.partner_id.id:
    #                 partners.append(
    #                     leave_sudo.employee_id.parent_id.user_id.partner_id.id)
    #             if leave_sudo.employee_id.leave_manager_id.partner_id.id:
    #                 partners.append(
    #                     leave_sudo.employee_id.leave_manager_id.partner_id.id)
    #             leave_sudo.message_subscribe(partner_ids=partners)
    #             if leave_sudo.employee_id and leave_sudo.holiday_status_id and leave_sudo.holiday_status_id.validation_type == 'direct_director':
    #                 leave_sudo.send_for_approval()
    #             if emp_obj.new_divisions.name == 'Technical':
    #                 channel_id = self.env.ref(
    #                     'custom_timeoff.technical_time_off_notifications')
    #                 user_id = emp_obj.user_id.partner_id.id
    #                 direct_manager_id = emp_obj.direct_manager_id.partner_id
    #                 time_off_officer_id = time_off_type_obj.responsible_id.partner_id
    #                 user_notified = [direct_manager_id.id,
    #                                  time_off_officer_id.id]
    #                 notification_ids = []
    #                 for user in user_notified:
    #                     notification_id = [((0, 0, {
    #                         'res_partner_id': user,
    #                         'notification_type': 'inbox'}))]
    #                     notification_ids.append(notification_id)
    #                 message = _(
    #                     "%s has requested %d days on the time off request <a href=# data-oe-model=hr.leave "
    #                     "data-oe-id=%d>%s</a>.") % (
    #                               emp_obj.name,
    #                               res.number_of_days,
    #                               res.id,
    #                               res.name)
    #                 channel_id.message_post(author_id=user_id,
    #                                         body=_(message),
    #                                         message_type='notification',
    #                                         subtype='mail.mt_comment',
    #                                         notification_ids=notification_ids,
    #                                         partner_ids=[direct_manager_id.id,
    #                                                      time_off_officer_id.id],
    #                                         )
    #
    #             else:
    #                 channel_id = self.env.ref(
    #                     'custom_timeoff.general_time_off_notifications')
    #                 user_id = emp_obj.user_id.partner_id.id
    #                 direct_manager_id = emp_obj.direct_manager_id.partner_id
    #                 time_off_officer_id = time_off_type_obj.responsible_id.partner_id
    #                 ab = [direct_manager_id.id, time_off_officer_id.id]
    #                 notification_ids = []
    #                 for rec in ab:
    #                     notification_id = [((0, 0, {
    #                         'res_partner_id': rec,
    #                         'notification_type': 'inbox'}))]
    #                     notification_ids.append(notification_id)
    #                 message = _(
    #                     "%s has requested %d days on the time off request <a href=# data-oe-model=hr.leave "
    #                     "data-oe-id=%d>%s</a>.") % (
    #                               emp_obj.name,
    #                               res.number_of_days,
    #                               res.id,
    #                               res.name)
    #                 channel_id.message_post(author_id=user_id,
    #                                         body=_(message),
    #                                         message_type='notification',
    #                                         subtype='mail.mt_comment',
    #                                         notification_ids=notification_ids,
    #                                         partner_ids=[direct_manager_id.id,
    #                                                      time_off_officer_id.id],
    #                                         )
    #             res.state = 'direct_manager'
    #             return res
    #
    #     elif validation_type == 'time_off_responsible':
    #         if leave_limit == 0 or number_of_days <= leave_limit:
    #             res = super(CustomHrLeave, self).create(vals)
    #             leave_sudo = res.sudo()
    #             partners = []
    #             if leave_sudo.employee_id.direct_manager_id.partner_id.id:
    #                 partners.append(
    #                     leave_sudo.employee_id.direct_manager_id.partner_id.id)
    #             if leave_sudo.employee_id.second_direct_manager_id.partner_id.id:
    #                 partners.append(
    #                     leave_sudo.employee_id.second_direct_manager_id.partner_id.id)
    #             if leave_sudo.employee_id.director_id.partner_id.id:
    #                 partners.append(
    #                     leave_sudo.employee_id.director_id.partner_id.id)
    #             if leave_sudo.employee_id.parent_id.user_id.partner_id.id:
    #                 partners.append(
    #                     leave_sudo.employee_id.parent_id.user_id.partner_id.id)
    #             if leave_sudo.employee_id.leave_manager_id.partner_id.id:
    #                 partners.append(
    #                     leave_sudo.employee_id.leave_manager_id.partner_id.id)
    #             leave_sudo.message_subscribe(partner_ids=partners)
    #             if leave_sudo.employee_id and leave_sudo.holiday_status_id and leave_sudo.holiday_status_id.validation_type == 'direct_director':
    #                 leave_sudo.send_for_approval()
    #             return res
    #         else:
    #             res = super(CustomHrLeave, self).create(vals)
    #             leave_sudo = res.sudo()
    #             partners = []
    #             if leave_sudo.employee_id.direct_manager_id.partner_id.id:
    #                 partners.append(
    #                     leave_sudo.employee_id.direct_manager_id.partner_id.id)
    #             if leave_sudo.employee_id.second_direct_manager_id.partner_id.id:
    #                 partners.append(
    #                     leave_sudo.employee_id.second_direct_manager_id.partner_id.id)
    #             if leave_sudo.employee_id.director_id.partner_id.id:
    #                 partners.append(
    #                     leave_sudo.employee_id.director_id.partner_id.id)
    #             if leave_sudo.employee_id.parent_id.user_id.partner_id.id:
    #                 partners.append(
    #                     leave_sudo.employee_id.parent_id.user_id.partner_id.id)
    #             if leave_sudo.employee_id.leave_manager_id.partner_id.id:
    #                 partners.append(
    #                     leave_sudo.employee_id.leave_manager_id.partner_id.id)
    #             leave_sudo.message_subscribe(partner_ids=partners)
    #             if leave_sudo.employee_id and leave_sudo.holiday_status_id and leave_sudo.holiday_status_id.validation_type == 'direct_director':
    #                 leave_sudo.send_for_approval()
    #             if emp_obj.new_divisions.name == 'Technical':
    #                 channel_id = self.env.ref(
    #                     'custom_timeoff.technical_time_off_notifications')
    #                 user_id = emp_obj.user_id.partner_id.id
    #                 time_off_responsible = emp_obj.leave_manager_id.partner_id
    #
    #                 notification_ids = [((0, 0, {
    #                     'res_partner_id': time_off_responsible.id,
    #                     'notification_type': 'inbox'}))]
    #
    #                 message = _(
    #                     "%s has requested %d days on the time off request <a href=# data-oe-model=hr.leave "
    #                     "data-oe-id=%d>%s</a>.") % (
    #                               emp_obj.name,
    #                               res.number_of_days,
    #                               res.id,
    #                               res.name)
    #                 channel_id.message_post(author_id=user_id,
    #                                         body=_(message),
    #                                         message_type='notification',
    #                                         subtype='mail.mt_comment',
    #                                         notification_ids=notification_ids,
    #                                         partner_ids=[
    #                                             time_off_responsible.id],
    #                                         )
    #
    #             else:
    #                 channel_id = self.env.ref(
    #                     'custom_timeoff.general_time_off_notifications')
    #                 user_id = emp_obj.user_id.partner_id.id
    #                 time_off_responsible = emp_obj.leave_manager_id.partner_id
    #                 notification_ids = [((0, 0, {
    #                     'res_partner_id': time_off_responsible.id,
    #                     'notification_type': 'inbox'}))]
    #                 message = _(
    #                     "%s has requested %d days on the time off request <a href=# data-oe-model=hr.leave "
    #                     "data-oe-id=%d>%s</a>.") % (
    #                               emp_obj.name,
    #                               res.number_of_days,
    #                               res.id,
    #                               res.name)
    #                 channel_id.message_post(author_id=user_id,
    #                                         body=_(message),
    #                                         message_type='notification',
    #                                         subtype='mail.mt_comment',
    #                                         notification_ids=notification_ids,
    #                                         partner_ids=[
    #                                             time_off_responsible.id],
    #                                         )
    #             return res
    #     elif validation_type == 'time_off_responsible_and_time_off_officer':
    #         if leave_limit == 0 or number_of_days <= leave_limit:
    #             res = super(CustomHrLeave, self).create(vals)
    #             leave_sudo = res.sudo()
    #             partners = []
    #             if leave_sudo.employee_id.direct_manager_id.partner_id.id:
    #                 partners.append(
    #                     leave_sudo.employee_id.direct_manager_id.partner_id.id)
    #             if leave_sudo.employee_id.second_direct_manager_id.partner_id.id:
    #                 partners.append(
    #                     leave_sudo.employee_id.second_direct_manager_id.partner_id.id)
    #             if leave_sudo.employee_id.director_id.partner_id.id:
    #                 partners.append(
    #                     leave_sudo.employee_id.director_id.partner_id.id)
    #             if leave_sudo.employee_id.parent_id.user_id.partner_id.id:
    #                 partners.append(
    #                     leave_sudo.employee_id.parent_id.user_id.partner_id.id)
    #             if leave_sudo.employee_id.leave_manager_id.partner_id.id:
    #                 partners.append(
    #                     leave_sudo.employee_id.leave_manager_id.partner_id.id)
    #             leave_sudo.message_subscribe(partner_ids=partners)
    #             if leave_sudo.employee_id and leave_sudo.holiday_status_id and leave_sudo.holiday_status_id.validation_type == 'direct_director':
    #                 leave_sudo.send_for_approval()
    #             res.state = 'time_off_responsible'
    #             return res
    #
    #         else:
    #             res = super(CustomHrLeave, self).create(vals)
    #             leave_sudo = res.sudo()
    #             partners = []
    #             if leave_sudo.employee_id.direct_manager_id.partner_id.id:
    #                 partners.append(
    #                     leave_sudo.employee_id.direct_manager_id.partner_id.id)
    #             if leave_sudo.employee_id.second_direct_manager_id.partner_id.id:
    #                 partners.append(
    #                     leave_sudo.employee_id.second_direct_manager_id.partner_id.id)
    #             if leave_sudo.employee_id.director_id.partner_id.id:
    #                 partners.append(
    #                     leave_sudo.employee_id.director_id.partner_id.id)
    #             if leave_sudo.employee_id.parent_id.user_id.partner_id.id:
    #                 partners.append(
    #                     leave_sudo.employee_id.parent_id.user_id.partner_id.id)
    #             if leave_sudo.employee_id.leave_manager_id.partner_id.id:
    #                 partners.append(
    #                     leave_sudo.employee_id.leave_manager_id.partner_id.id)
    #             leave_sudo.message_subscribe(partner_ids=partners)
    #             if leave_sudo.employee_id and leave_sudo.holiday_status_id and leave_sudo.holiday_status_id.validation_type == 'direct_director':
    #                 leave_sudo.send_for_approval()
    #             if emp_obj.new_divisions.name == 'Technical':
    #                 channel_id = self.env.ref(
    #                     'custom_timeoff.technical_time_off_notifications')
    #                 user_id = emp_obj.user_id.partner_id.id
    #                 time_off_responsible = emp_obj.leave_manager_id.partner_id
    #                 time_off_officer_id = time_off_type_obj.responsible_id.partner_id
    #                 user_notified = [time_off_responsible.id,
    #                                  time_off_officer_id.id]
    #                 notification_ids = []
    #                 for rec in user_notified:
    #                     notification_id = [((0, 0, {
    #                         'res_partner_id': rec,
    #                         'notification_type': 'inbox'}))]
    #                     notification_ids.append(notification_id)
    #                 message = _(
    #                     "%s has requested %d days on the time off request <a href=# data-oe-model=hr.leave "
    #                     "data-oe-id=%d>%s</a>.") % (
    #                               emp_obj.name,
    #                               res.number_of_days,
    #                               res.id,
    #                               res.name)
    #                 channel_id.message_post(author_id=user_id,
    #                                         body=_(message),
    #                                         message_type='notification',
    #                                         subtype='mail.mt_comment',
    #                                         notification_ids=notification_ids,
    #                                         partner_ids=[
    #                                             time_off_responsible.id,
    #                                             time_off_officer_id.id],
    #                                         )
    #
    #             else:
    #                 channel_id = self.env.ref(
    #                     'custom_timeoff.general_time_off_notifications')
    #                 user_id = emp_obj.user_id.partner_id.id
    #                 time_off_responsible = emp_obj.leave_manager_id.partner_id
    #                 time_off_officer_id = time_off_type_obj.responsible_id.partner_id
    #                 user_notified = [time_off_responsible.id,
    #                                  time_off_officer_id.id]
    #                 notification_ids = []
    #                 for rec in user_notified:
    #                     notification_id = [((0, 0, {
    #                         'res_partner_id': rec,
    #                         'notification_type': 'inbox'}))]
    #                     notification_ids.append((notification_id))
    #                 message = _(
    #                     "%s has requested %d days on the time off request <a href=# data-oe-model=hr.leave "
    #                     "data-oe-id=%d>%s</a>.") % (
    #                               emp_obj.name,
    #                               res.number_of_days,
    #                               res.id,
    #                               res.name)
    #                 channel_id.message_post(author_id=user_id,
    #                                         body=_(message),
    #                                         message_type='notification',
    #                                         subtype='mail.mt_comment',
    #                                         notification_ids=notification_ids,
    #                                         partner_ids=[
    #                                             time_off_responsible.id,
    #                                             time_off_officer_id.id],
    #                                         )
    #             res.state = 'time_off_responsible'
    #             return res
    #     elif validation_type == 'direct_manager_and_second_direct_manager':
    #         if leave_limit == 0 or number_of_days <= leave_limit:
    #             res = super(CustomHrLeave, self).create(vals)
    #             leave_sudo = res.sudo()
    #             partners = []
    #             if leave_sudo.employee_id.direct_manager_id.partner_id.id:
    #                 partners.append(
    #                     leave_sudo.employee_id.direct_manager_id.partner_id.id)
    #             if leave_sudo.employee_id.second_direct_manager_id.partner_id.id:
    #                 partners.append(
    #                     leave_sudo.employee_id.second_direct_manager_id.partner_id.id)
    #             if leave_sudo.employee_id.director_id.partner_id.id:
    #                 partners.append(
    #                     leave_sudo.employee_id.director_id.partner_id.id)
    #             if leave_sudo.employee_id.parent_id.user_id.partner_id.id:
    #                 partners.append(
    #                     leave_sudo.employee_id.parent_id.user_id.partner_id.id)
    #             if leave_sudo.employee_id.leave_manager_id.partner_id.id:
    #                 partners.append(
    #                     leave_sudo.employee_id.leave_manager_id.partner_id.id)
    #             leave_sudo.message_subscribe(partner_ids=partners)
    #             if leave_sudo.employee_id and leave_sudo.holiday_status_id and leave_sudo.holiday_status_id.validation_type == 'direct_director':
    #                 leave_sudo.send_for_approval()
    #             res.state = 'direct_manager'
    #             return res
    #
    #         else:
    #             res = super(CustomHrLeave, self).create(vals)
    #             leave_sudo = res.sudo()
    #             partners = []
    #             if leave_sudo.employee_id.direct_manager_id.partner_id.id:
    #                 partners.append(
    #                     leave_sudo.employee_id.direct_manager_id.partner_id.id)
    #             if leave_sudo.employee_id.second_direct_manager_id.partner_id.id:
    #                 partners.append(
    #                     leave_sudo.employee_id.second_direct_manager_id.partner_id.id)
    #             if leave_sudo.employee_id.director_id.partner_id.id:
    #                 partners.append(
    #                     leave_sudo.employee_id.director_id.partner_id.id)
    #             if leave_sudo.employee_id.parent_id.user_id.partner_id.id:
    #                 partners.append(
    #                     leave_sudo.employee_id.parent_id.user_id.partner_id.id)
    #             if leave_sudo.employee_id.leave_manager_id.partner_id.id:
    #                 partners.append(
    #                     leave_sudo.employee_id.leave_manager_id.partner_id.id)
    #             leave_sudo.message_subscribe(partner_ids=partners)
    #             if leave_sudo.employee_id and leave_sudo.holiday_status_id and leave_sudo.holiday_status_id.validation_type == 'direct_director':
    #                 leave_sudo.send_for_approval()
    #             if emp_obj.new_divisions.name == 'Technical':
    #                 channel_id = self.env.ref(
    #                     'custom_timeoff.technical_time_off_notifications')
    #                 user_id = emp_obj.user_id.partner_id.id
    #                 direct_manager = emp_obj.direct_manager_id.partner_id
    #                 second_direct_manager = emp_obj.second_direct_manager_id.partner_id
    #                 user_notified = [direct_manager.id,
    #                                  second_direct_manager.id]
    #                 notification_ids = []
    #                 for rec in user_notified:
    #                     notification_id = [((0, 0, {
    #                         'res_partner_id': rec,
    #                         'notification_type': 'inbox'}))]
    #                     notification_ids.append(notification_id)
    #                 message = _(
    #                     "%s has requested %d days on the time off request <a href=# data-oe-model=hr.leave "
    #                     "data-oe-id=%d>%s</a>.") % (
    #                               emp_obj.name,
    #                               res.number_of_days,
    #                               res.id,
    #                               res.name)
    #                 channel_id.message_post(author_id=user_id,
    #                                         body=_(message),
    #                                         message_type='notification',
    #                                         subtype='mail.mt_comment',
    #                                         notification_ids=notification_ids,
    #                                         partner_ids=[direct_manager.id,
    #                                                      second_direct_manager.id],
    #                                         )
    #
    #             else:
    #                 channel_id = self.env.ref(
    #                     'custom_timeoff.general_time_off_notifications')
    #                 user_id = emp_obj.user_id.partner_id.id
    #                 direct_manager = emp_obj.direct_manager_id.partner_id
    #                 second_direct_manager = emp_obj.second_direct_manager_id.partner_id
    #                 user_notified = [direct_manager.id,
    #                                  second_direct_manager.id]
    #                 notification_ids = []
    #                 for rec in user_notified:
    #                     notification_id = [((0, 0, {
    #                         'res_partner_id': rec,
    #                         'notification_type': 'inbox'}))]
    #                     notification_ids.append((notification_id))
    #                 message = _(
    #                     "%s has requested %d days on the time off request <a href=# data-oe-model=hr.leave "
    #                     "data-oe-id=%d>%s</a>.") % (
    #                               emp_obj.name,
    #                               res.number_of_days,
    #                               res.id,
    #                               res.name)
    #                 channel_id.message_post(author_id=user_id,
    #                                         body=_(message),
    #                                         message_type='notification',
    #                                         subtype='mail.mt_comment',
    #                                         notification_ids=notification_ids,
    #                                         partner_ids=[direct_manager.id,
    #                                                      second_direct_manager.id],
    #                                         )
    #             res.state = 'direct_manager'
    #             return res
    #     elif validation_type == 'direct_and_second_direct_and_time_off_officer':
    #         if leave_limit == 0 or number_of_days <= leave_limit:
    #             res = super(CustomHrLeave, self).create(vals)
    #             leave_sudo = res.sudo()
    #             partners = []
    #             if leave_sudo.employee_id.direct_manager_id.partner_id.id:
    #                 partners.append(
    #                     leave_sudo.employee_id.direct_manager_id.partner_id.id)
    #             if leave_sudo.employee_id.second_direct_manager_id.partner_id.id:
    #                 partners.append(
    #                     leave_sudo.employee_id.second_direct_manager_id.partner_id.id)
    #             if leave_sudo.employee_id.director_id.partner_id.id:
    #                 partners.append(
    #                     leave_sudo.employee_id.director_id.partner_id.id)
    #             if leave_sudo.employee_id.parent_id.user_id.partner_id.id:
    #                 partners.append(
    #                     leave_sudo.employee_id.parent_id.user_id.partner_id.id)
    #             if leave_sudo.employee_id.leave_manager_id.partner_id.id:
    #                 partners.append(
    #                     leave_sudo.employee_id.leave_manager_id.partner_id.id)
    #             leave_sudo.message_subscribe(partner_ids=partners)
    #             if leave_sudo.employee_id and leave_sudo.holiday_status_id and leave_sudo.holiday_status_id.validation_type == 'direct_director':
    #                 leave_sudo.send_for_approval()
    #             res.state = 'direct_manager'
    #             return res
    #
    #         else:
    #             res = super(CustomHrLeave, self).create(vals)
    #             leave_sudo = res.sudo()
    #             partners = []
    #             if leave_sudo.employee_id.direct_manager_id.partner_id.id:
    #                 partners.append(
    #                     leave_sudo.employee_id.direct_manager_id.partner_id.id)
    #             if leave_sudo.employee_id.second_direct_manager_id.partner_id.id:
    #                 partners.append(
    #                     leave_sudo.employee_id.second_direct_manager_id.partner_id.id)
    #             if leave_sudo.employee_id.director_id.partner_id.id:
    #                 partners.append(
    #                     leave_sudo.employee_id.director_id.partner_id.id)
    #             if leave_sudo.employee_id.parent_id.user_id.partner_id.id:
    #                 partners.append(
    #                     leave_sudo.employee_id.parent_id.user_id.partner_id.id)
    #             if leave_sudo.employee_id.leave_manager_id.partner_id.id:
    #                 partners.append(
    #                     leave_sudo.employee_id.leave_manager_id.partner_id.id)
    #             leave_sudo.message_subscribe(partner_ids=partners)
    #             if leave_sudo.employee_id and leave_sudo.holiday_status_id and leave_sudo.holiday_status_id.validation_type == 'direct_director':
    #                 leave_sudo.send_for_approval()
    #             if emp_obj.new_divisions.name == 'Technical':
    #                 channel_id = self.env.ref(
    #                     'custom_timeoff.technical_time_off_notifications')
    #                 user_id = emp_obj.user_id.partner_id.id
    #                 direct_manager = emp_obj.direct_manager_id.partner_id
    #                 second_direct_manager = emp_obj.second_direct_manager_id.partner_id
    #                 time_off_officer_id = time_off_type_obj.responsible_id.partner_id
    #                 user_notified = [direct_manager.id,
    #                                  second_direct_manager.id,
    #                                  time_off_officer_id.id]
    #                 notification_ids = []
    #                 for rec in user_notified:
    #                     notification_id = [((0, 0, {
    #                         'res_partner_id': rec,
    #                         'notification_type': 'inbox'}))]
    #                     notification_ids.append(notification_id)
    #                 message = _(
    #                     "%s has requested %d days on the time off request <a href=# data-oe-model=hr.leave "
    #                     "data-oe-id=%d>%s</a>.") % (
    #                               emp_obj.name,
    #                               res.number_of_days,
    #                               res.id,
    #                               res.name)
    #                 channel_id.message_post(author_id=user_id,
    #                                         body=_(message),
    #                                         message_type='notification',
    #                                         subtype='mail.mt_comment',
    #                                         notification_ids=notification_ids,
    #                                         partner_ids=[direct_manager.id,
    #                                                      second_direct_manager.id,
    #                                                      time_off_officer_id.id],
    #                                         )
    #
    #             else:
    #                 channel_id = self.env.ref(
    #                     'custom_timeoff.general_time_off_notifications')
    #                 user_id = emp_obj.user_id.partner_id.id
    #                 direct_manager = emp_obj.direct_manager_id.partner_id
    #                 second_direct_manager = emp_obj.second_direct_manager_id.partner_id
    #                 time_off_officer_id = time_off_type_obj.responsible_id.partner_id
    #                 user_notified = [direct_manager.id,
    #                                  second_direct_manager.id,
    #                                  time_off_officer_id.id]
    #                 notification_ids = []
    #                 for rec in user_notified:
    #                     notification_id = [((0, 0, {
    #                         'res_partner_id': rec,
    #                         'notification_type': 'inbox'}))]
    #                     notification_ids.append((notification_id))
    #                 message = _(
    #                     "%s has requested %d days on the time off request <a href=# data-oe-model=hr.leave "
    #                     "data-oe-id=%d>%s</a>.") % (
    #                               emp_obj.name,
    #                               res.number_of_days,
    #                               res.id,
    #                               res.name)
    #                 channel_id.message_post(author_id=user_id,
    #                                         body=_(message),
    #                                         message_type='notification',
    #                                         subtype='mail.mt_comment',
    #                                         notification_ids=notification_ids,
    #                                         partner_ids=[direct_manager.id,
    #                                                      second_direct_manager.id,
    #                                                      time_off_officer_id.id],
    #                                         )
    #             res.state = 'direct_manager'
    #             return res
    #     elif validation_type == 'hr':
    #         if leave_limit == 0 or number_of_days <= leave_limit:
    #             res = super(CustomHrLeave, self).create(vals)
    #             leave_sudo = res.sudo()
    #             partners = []
    #             if leave_sudo.employee_id.direct_manager_id.partner_id.id:
    #                 partners.append(
    #                     leave_sudo.employee_id.direct_manager_id.partner_id.id)
    #             if leave_sudo.employee_id.second_direct_manager_id.partner_id.id:
    #                 partners.append(
    #                     leave_sudo.employee_id.second_direct_manager_id.partner_id.id)
    #             if leave_sudo.employee_id.director_id.partner_id.id:
    #                 partners.append(
    #                     leave_sudo.employee_id.director_id.partner_id.id)
    #             if leave_sudo.employee_id.parent_id.user_id.partner_id.id:
    #                 partners.append(
    #                     leave_sudo.employee_id.parent_id.user_id.partner_id.id)
    #             if leave_sudo.employee_id.leave_manager_id.partner_id.id:
    #                 partners.append(
    #                     leave_sudo.employee_id.leave_manager_id.partner_id.id)
    #             leave_sudo.message_subscribe(partner_ids=partners)
    #             if leave_sudo.employee_id and leave_sudo.holiday_status_id and leave_sudo.holiday_status_id.leave_validation_type == 'direct_director':
    #                 leave_sudo.send_for_approval()
    #             return res
    #
    #         else:
    #             res = super(CustomHrLeave, self).create(vals)
    #             leave_sudo = res.sudo()
    #             partners = []
    #             if leave_sudo.employee_id.direct_manager_id.partner_id.id:
    #                 partners.append(
    #                     leave_sudo.employee_id.direct_manager_id.partner_id.id)
    #             if leave_sudo.employee_id.second_direct_manager_id.partner_id.id:
    #                 partners.append(
    #                     leave_sudo.employee_id.second_direct_manager_id.partner_id.id)
    #             if leave_sudo.employee_id.director_id.partner_id.id:
    #                 partners.append(
    #                     leave_sudo.employee_id.director_id.partner_id.id)
    #             if leave_sudo.employee_id.parent_id.user_id.partner_id.id:
    #                 partners.append(
    #                     leave_sudo.employee_id.parent_id.user_id.partner_id.id)
    #             if leave_sudo.employee_id.leave_manager_id.partner_id.id:
    #                 partners.append(
    #                     leave_sudo.employee_id.leave_manager_id.partner_id.id)
    #             leave_sudo.message_subscribe(partner_ids=partners)
    #             if leave_sudo.employee_id and leave_sudo.holiday_status_id and leave_sudo.holiday_status_id.validation_type == 'direct_director':
    #                 leave_sudo.send_for_approval()
    #             if emp_obj.new_divisions.name == 'Technical':
    #                 channel_id = self.env.ref(
    #                     'custom_timeoff.technical_time_off_notifications')
    #                 user_id = emp_obj.user_id.partner_id.id
    #                 emp_user_id = time_off_type_obj.responsible_id.partner_id
    #                 notification_ids = [((0, 0, {
    #                     'res_partner_id': emp_user_id.id,
    #                     'notification_type': 'inbox'}))]
    #                 message = _(
    #                     "%s has requested %d days on the time off request <a href=# data-oe-model=hr.leave "
    #                     "data-oe-id=%d>%s</a>.") % (
    #                               emp_obj.name,
    #                               res.number_of_days,
    #                               res.id,
    #                               res.name)
    #                 channel_id.message_post(author_id=user_id,
    #                                         body=_(message),
    #                                         message_type='notification',
    #                                         subtype='mail.mt_comment',
    #                                         notification_ids=notification_ids,
    #                                         partner_ids=[emp_user_id.id],
    #                                         )
    #
    #             else:
    #                 channel_id = self.env.ref(
    #                     'custom_timeoff.general_time_off_notifications')
    #                 user_id = emp_obj.user_id.partner_id.id
    #                 emp_user_id = time_off_type_obj.responsible_id.partner_id
    #                 notification_ids = [((0, 0, {
    #                     'res_partner_id': emp_user_id.id,
    #                     'notification_type': 'inbox'}))]
    #                 message = _(
    #                     "%s has requested %d days on the time off request <a href=# data-oe-model=hr.leave "
    #                     "data-oe-id=%d>%s</a>.") % (
    #                               emp_obj.name,
    #                               res.number_of_days,
    #                               res.id,
    #                               res.name)
    #                 channel_id.message_post(author_id=user_id,
    #                                         body=_(message),
    #                                         message_type='notification',
    #                                         subtype='mail.mt_comment',
    #                                         notification_ids=notification_ids,
    #                                         partner_ids=[emp_user_id.id],
    #                                         )
    #             return res
    #
    #     elif validation_type == 'manager':
    #         if leave_limit == 0 or number_of_days <= leave_limit:
    #             res = super(CustomHrLeave, self).create(vals)
    #             leave_sudo = res.sudo()
    #             partners = []
    #             if leave_sudo.employee_id.direct_manager_id.partner_id.id:
    #                 partners.append(
    #                     leave_sudo.employee_id.direct_manager_id.partner_id.id)
    #             if leave_sudo.employee_id.second_direct_manager_id.partner_id.id:
    #                 partners.append(
    #                     leave_sudo.employee_id.second_direct_manager_id.partner_id.id)
    #             if leave_sudo.employee_id.director_id.partner_id.id:
    #                 partners.append(
    #                     leave_sudo.employee_id.director_id.partner_id.id)
    #             if leave_sudo.employee_id.parent_id.user_id.partner_id.id:
    #                 partners.append(
    #                     leave_sudo.employee_id.parent_id.user_id.partner_id.id)
    #             if leave_sudo.employee_id.leave_manager_id.partner_id.id:
    #                 partners.append(
    #                     leave_sudo.employee_id.leave_manager_id.partner_id.id)
    #             leave_sudo.message_subscribe(partner_ids=partners)
    #             if leave_sudo.employee_id and leave_sudo.holiday_status_id and leave_sudo.holiday_status_id.validation_type == 'direct_director':
    #                 leave_sudo.send_for_approval()
    #             return res
    #
    #         else:
    #             res = super(CustomHrLeave, self).create(vals)
    #             leave_sudo = res.sudo()
    #             partners = []
    #             if leave_sudo.employee_id.direct_manager_id.partner_id.id:
    #                 partners.append(
    #                     leave_sudo.employee_id.direct_manager_id.partner_id.id)
    #             if leave_sudo.employee_id.second_direct_manager_id.partner_id.id:
    #                 partners.append(
    #                     leave_sudo.employee_id.second_direct_manager_id.partner_id.id)
    #             if leave_sudo.employee_id.director_id.partner_id.id:
    #                 partners.append(
    #                     leave_sudo.employee_id.director_id.partner_id.id)
    #             if leave_sudo.employee_id.parent_id.user_id.partner_id.id:
    #                 partners.append(
    #                     leave_sudo.employee_id.parent_id.user_id.partner_id.id)
    #             if leave_sudo.employee_id.leave_manager_id.partner_id.id:
    #                 partners.append(
    #                     leave_sudo.employee_id.leave_manager_id.partner_id.id)
    #             leave_sudo.message_subscribe(partner_ids=partners)
    #             if leave_sudo.employee_id and leave_sudo.holiday_status_id and leave_sudo.holiday_status_id.validation_type == 'direct_director':
    #                 leave_sudo.send_for_approval()
    #             if emp_obj.new_divisions.name == 'Technical':
    #                 channel_id = self.env.ref(
    #                     'custom_timeoff.technical_time_off_notifications')
    #                 user_id = emp_obj.user_id.partner_id.id
    #                 emp_user_id = emp_obj.parent_id.user_id.partner_id
    #                 notification_ids = [((0, 0, {
    #                     'res_partner_id': emp_user_id.id,
    #                     'notification_type': 'inbox'}))]
    #                 message = _(
    #                     "%s has requested %d days on the time off request <a href=# data-oe-model=hr.leave "
    #                     "data-oe-id=%d>%s</a>.") % (
    #                               emp_obj.name,
    #                               res.number_of_days,
    #                               res.id,
    #                               res.name)
    #                 channel_id.message_post(author_id=user_id,
    #                                         body=_(message),
    #                                         message_type='notification',
    #                                         subtype='mail.mt_comment',
    #                                         notification_ids=notification_ids,
    #                                         partner_ids=[emp_user_id.id],
    #                                         )
    #             else:
    #                 channel_id = self.env.ref(
    #                     'custom_timeoff.general_time_off_notifications')
    #                 user_id = emp_obj.user_id.partner_id.id
    #                 emp_user_id = emp_obj.parent_id.user_id.partner_id
    #                 notification_ids = [((0, 0, {
    #                     'res_partner_id': emp_user_id.id,
    #                     'notification_type': 'inbox'}))]
    #                 message = _(
    #                     "%s has requested %d days on the time off request <a href=# data-oe-model=hr.leave "
    #                     "data-oe-id=%d>%s</a>.") % (
    #                               emp_obj.name,
    #                               res.number_of_days,
    #                               res.id,
    #                               res.name)
    #                 channel_id.message_post(author_id=user_id,
    #                                         body=_(message),
    #                                         message_type='notification',
    #                                         subtype='mail.mt_comment',
    #                                         notification_ids=notification_ids,
    #                                         partner_ids=[emp_user_id.id],
    #                                         )
    #             return res
    #
    #     elif validation_type == 'both':
    #         if leave_limit == 0 or number_of_days <= leave_limit:
    #             res = super(CustomHrLeave, self).create(vals)
    #             leave_sudo = res.sudo()
    #             partners = []
    #             if leave_sudo.employee_id.direct_manager_id.partner_id.id:
    #                 partners.append(
    #                     leave_sudo.employee_id.direct_manager_id.partner_id.id)
    #             if leave_sudo.employee_id.second_direct_manager_id.partner_id.id:
    #                 partners.append(
    #                     leave_sudo.employee_id.second_direct_manager_id.partner_id.id)
    #             if leave_sudo.employee_id.director_id.partner_id.id:
    #                 partners.append(
    #                     leave_sudo.employee_id.director_id.partner_id.id)
    #             if leave_sudo.employee_id.parent_id.user_id.partner_id.id:
    #                 partners.append(
    #                     leave_sudo.employee_id.parent_id.user_id.partner_id.id)
    #             if leave_sudo.employee_id.leave_manager_id.partner_id.id:
    #                 partners.append(
    #                     leave_sudo.employee_id.leave_manager_id.partner_id.id)
    #             leave_sudo.message_subscribe(partner_ids=partners)
    #             if leave_sudo.employee_id and leave_sudo.holiday_status_id and leave_sudo.holiday_status_id.validation_type == 'direct_director':
    #                 leave_sudo.send_for_approval()
    #             res.state = 'manager'
    #             return res
    #
    #         else:
    #             res = super(CustomHrLeave, self).create(vals)
    #             leave_sudo = res.sudo()
    #             partners = []
    #             if leave_sudo.employee_id.direct_manager_id.partner_id.id:
    #                 partners.append(
    #                     leave_sudo.employee_id.direct_manager_id.partner_id.id)
    #             if leave_sudo.employee_id.second_direct_manager_id.partner_id.id:
    #                 partners.append(
    #                     leave_sudo.employee_id.second_direct_manager_id.partner_id.id)
    #             if leave_sudo.employee_id.director_id.partner_id.id:
    #                 partners.append(
    #                     leave_sudo.employee_id.director_id.partner_id.id)
    #             if leave_sudo.employee_id.parent_id.user_id.partner_id.id:
    #                 partners.append(
    #                     leave_sudo.employee_id.parent_id.user_id.partner_id.id)
    #             if leave_sudo.employee_id.leave_manager_id.partner_id.id:
    #                 partners.append(
    #                     leave_sudo.employee_id.leave_manager_id.partner_id.id)
    #             leave_sudo.message_subscribe(partner_ids=partners)
    #             if leave_sudo.employee_id and leave_sudo.holiday_status_id and leave_sudo.holiday_status_id.validation_type == 'direct_director':
    #                 leave_sudo.send_for_approval()
    #             if emp_obj.new_divisions.name == 'Technical':
    #                 channel_id = self.env.ref(
    #                     'custom_timeoff.technical_time_off_notifications')
    #                 user_id = emp_obj.user_id.partner_id.id
    #                 emp_manager_id = emp_obj.parent_id.user_id.partner_id
    #                 time_off_officer_id = time_off_type_obj.responsible_id.partner_id
    #                 user_notified = [emp_manager_id.id, time_off_officer_id.id]
    #                 notification_ids = []
    #                 for rec in user_notified:
    #                     notification_id = [((0, 0, {
    #                         'res_partner_id': rec,
    #                         'notification_type': 'inbox'}))]
    #                     notification_ids.append(notification_id)
    #                 message = _(
    #                     "%s has requested %d days on the time off request <a href=# data-oe-model=hr.leave "
    #                     "data-oe-id=%d>%s</a>.") % (
    #                               emp_obj.name,
    #                               res.number_of_days,
    #                               res.id,
    #                               res.name)
    #                 channel_id.message_post(author_id=user_id,
    #                                         body=_(message),
    #                                         message_type='notification',
    #                                         subtype='mail.mt_comment',
    #                                         notification_ids=notification_ids,
    #                                         partner_ids=[emp_manager_id.id,
    #                                                      time_off_officer_id.id],
    #                                         )
    #             else:
    #                 channel_id = self.env.ref(
    #                     'custom_timeoff.general_time_off_notifications')
    #                 user_id = emp_obj.user_id.partner_id.id
    #                 emp_manager_id = emp_obj.parent_id.user_id.partner_id
    #                 time_off_officer_id = time_off_type_obj.responsible_id.partner_id
    #                 notification_ids = []
    #                 for emp in [emp_manager_id.id, time_off_officer_id.id]:
    #                     notification_id = ((0, 0, {
    #                         'res_partner_id': emp,
    #                         'notification_type': 'inbox'}))
    #                     notification_ids.append(notification_id)
    #                 message = _(
    #                     "%s has requested %d days on the time off request <a href=# data-oe-model=hr.leave "
    #                     "data-oe-id=%d>%s</a>.") % (
    #                               emp_obj.name,
    #                               res.number_of_days,
    #                               res.id,
    #                               res.name)
    #                 channel_id.message_post(author_id=user_id,
    #                                         body=_(message),
    #                                         message_type='notification',
    #                                         subtype='mail.mt_comment',
    #                                         notification_ids=notification_ids,
    #                                         partner_ids=[emp_manager_id.id,
    #                                                      time_off_officer_id.id],
    #                                         )
    #             res.state = 'manager'
    #             return res
    #
    #     elif validation_type == 'direct_director':
    #         vals["employee_id"] = self.env.user.employee_id
    #         res = super(CustomHrLeave, self).create(vals)
    #         leave_sudo = res.sudo()
    #         partners = []
    #         if leave_sudo.employee_id.direct_manager_id.partner_id.id:
    #             partners.append(
    #                 leave_sudo.employee_id.direct_manager_id.partner_id.id)
    #         if leave_sudo.employee_id.second_direct_manager_id.partner_id.id:
    #             partners.append(
    #                 leave_sudo.employee_id.second_direct_manager_id.partner_id.id)
    #         if leave_sudo.employee_id.director_id.partner_id.id:
    #             partners.append(
    #                 leave_sudo.employee_id.director_id.partner_id.id)
    #         if leave_sudo.employee_id.parent_id.user_id.partner_id.id:
    #             partners.append(
    #                 leave_sudo.employee_id.parent_id.user_id.partner_id.id)
    #         if leave_sudo.employee_id.leave_manager_id.partner_id.id:
    #             partners.append(
    #                 leave_sudo.employee_id.leave_manager_id.partner_id.id)
    #         leave_sudo.message_subscribe(partner_ids=partners)
    #         if leave_sudo.employee_id and leave_sudo.holiday_status_id and leave_sudo.holiday_status_id.validation_type == 'direct_director':
    #             leave_sudo.send_for_approval()
    #         return res

    def _get_responsible_for_approval(self):
        self.ensure_one()
        responsible_users = self.env['res.users'].browse(SUPERUSER_ID)

        if self.validation_type == 'manager' and self.state == 'confirm':
            if self.employee_id.parent_id and self.employee_id.parent_id.user_id:
                responsible_users |= self.employee_id.parent_id.user_id

        elif self.validation_type == 'both':
            if self.employee_id.parent_id and self.employee_id.parent_id.user_id:
                responsible_users |= self.employee_id.parent_id.user_id
            if self.holiday_status_id.responsible_ids:
                responsible_users |= self.holiday_status_id.responsible_ids

        elif self.validation_type == 'hr':
            if self.holiday_status_id.responsible_ids:
                responsible_users = self.holiday_status_id.responsible_ids

        elif self.validation_type == 'direct_manager':
            if self.employee_id.direct_manager_id:
                responsible_users = self.employee_id.direct_manager_id

        elif self.validation_type == 'direct_manager_and_time_off_officer':
            if self.employee_id.direct_manager_id:
                responsible_users |= self.employee_id.direct_manager_id
            if self.holiday_status_id.responsible_ids:
                responsible_users |= self.holiday_status_id.responsible_ids

        elif self.validation_type == 'time_off_responsible':
            if self.employee_id.leave_manager_id:
                responsible_users = self.employee_id.leave_manager_id

        elif self.validation_type == 'time_off_responsible_and_time_off_officer':
            if self.employee_id.leave_manager_id:
                responsible_users |= self.employee_id.leave_manager_id
            if self.holiday_status_id.responsible_ids:
                responsible_users |= self.holiday_status_id.responsible_ids

        elif self.validation_type == 'direct_manager_and_second_direct_manager':
            if self.employee_id.direct_manager_id:
                responsible_users |= self.employee_id.direct_manager_id
            if self.employee_id.second_direct_manager_id:
                responsible_users |= self.employee_id.second_direct_manager_id

        elif self.validation_type == 'direct_and_second_direct_and_time_off_officer':
            if self.employee_id.direct_manager_id:
                responsible_users |= self.employee_id.direct_manager_id
            if self.employee_id.second_direct_manager_id:
                responsible_users |= self.employee_id.second_direct_manager_id
            if self.holiday_status_id.responsible_ids:
                responsible_users |= self.holiday_status_id.responsible_ids

        return responsible_users

    def _schedule_activity_for_users(self, activity_type, note, users):
        """Helper to schedule activities for given users + their deputies."""
        for user in users:
            self.activity_schedule(
                activity_type,
                note=note,
                user_id=user.id or self.env.user.id
            )
            # Handle deputy if available
            emp = getattr(user, 'emp_id', False)
            if emp and emp.timeoff_deputy and emp.timeoff_deputy.user_id:
                self.activity_schedule(
                    activity_type,
                    note=note,
                    user_id=emp.timeoff_deputy.user_id.id
                )

    @api.model
    def activity_update(self):
        to_clean, to_do = self.env['hr.leave'], self.env['hr.leave']
        for holiday in self:
            start = UTC.localize(holiday.date_from).astimezone(
                timezone(holiday.employee_id.tz or 'UTC'))
            end = UTC.localize(holiday.date_to).astimezone(
                timezone(holiday.employee_id.tz or 'UTC'))

            note = _('New %s Request created by %s from %s to %s') % (
                holiday.holiday_status_id.name,
                holiday.create_uid.name,
                start.strftime('%Y-%m-%d %H:%M'),
                end.strftime('%Y-%m-%d %H:%M')
            )

            validation_type = holiday.holiday_status_id.leave_validation_type

            if holiday.state == 'draft':
                to_clean |= holiday

            elif holiday.state == 'confirm':
                approvers = holiday.sudo()._get_responsible_for_approval()
                if validation_type == 'both':
                    if holiday.employee_id.parent_id and holiday.employee_id.parent_id.user_id:
                        approvers |= holiday.employee_id.parent_id.user_id

                holiday._schedule_activity_for_users(
                    'hr_holidays.mail_act_leave_approval', note, approvers)

            elif holiday.state == 'validate1':
                holiday.activity_feedback(
                    ['hr_holidays.mail_act_leave_approval'])
                approvers = holiday.sudo()._get_responsible_for_approval()
                holiday._schedule_activity_for_users(
                    'hr_holidays.mail_act_leave_second_approval', note,
                    approvers)

            elif holiday.state == 'validate':
                to_do |= holiday

            elif holiday.state == 'refuse':
                to_clean |= holiday
                note = _("Your request for leave is refused")
                if holiday.employee_id.user_id:
                    holiday.activity_schedule(
                        'custom_timeoff.mail_act_leave_request_refuse',
                        note=note,
                        user_id=holiday.employee_id.user_id.id
                    )

        if to_clean:
            to_clean.activity_unlink([
                'hr_holidays.mail_act_leave_approval',
                'hr_holidays.mail_act_leave_second_approval',
                'custom_timeoff.mail_act_leave_request_approve_time_off_officer',
                'custom_timeoff.mail_act_leave_request_approve_second_manager'
            ])

        if to_do:
            to_do.activity_feedback([
                'hr_holidays.mail_act_leave_approval',
                'hr_holidays.mail_act_leave_second_approval'
            ])
    def direct_manager_approve(self):
        if self.env.user.id == self.sudo().employee_id.direct_manager_id.id:
            if self.validation_type == 'direct_manager_and_second_direct_manager' or self.validation_type == 'direct_and_second_direct_and_time_off_officer':
                activity_id = self.env['mail.activity'].search(
                    [('res_id', '=', self.id),
                     ('activity_type_id', '=', self.env.ref(
                         'hr_holidays.mail_act_leave_approval').id)])
                activity_id.action_feedback(feedback="Approved DM")
                note = _("Your have a Time off request to approve")
                if not self.sudo().employee_id.second_direct_manager_id and self.validation_type == 'direct_manager_and_second_direct_manager':
                    self.write({'state': 'validate'})
                    note = _("Your request for leave is approved")
                    self.activity_schedule(
                        'custom_timeoff.mail_act_leave_request_approved',
                        note=note,
                        user_id=self.employee_id.user_id.id)
                elif not self.sudo().employee_id.second_direct_manager_id and self.validation_type == 'direct_and_second_direct_and_time_off_officer':
                    self.activity_schedule(
                        'custom_timeoff.mail_act_leave_request_approve_time_off_officer',
                        note=note,
                        user_id=self.holiday_status_id.responsible_id.id or self.env.user.id)
                    self.write({'state': 'time_off_officer'})
                else:
                    self.activity_schedule(
                        'custom_timeoff.mail_act_leave_request_approve_second_manager',
                        note=note,
                        user_id=self.sudo().employee_id.second_direct_manager_id.id or self.env.user.id)
                    self.write({'state': '2direct_manager'})

            elif self.validation_type == 'direct_director':
                for leave in self:
                    if leave and leave.sudo().employee_id and leave.sudo().employee_id.direct_manager_id.id and leave.sudo().employee_id.direct_manager_id.id != self.env.user.id:
                        raise ValidationError(
                            _("Only %s can approve leave for employee %s." % (
                                leave.sudo().employee_id.direct_manager_id.name,
                                leave.sudo().employee_id.name)))
                    # Second Direct manager
                    if leave and leave.sudo().employee_id and leave and leave.sudo().employee_id.second_direct_manager_id.id:
                        leave.write({'state': '2direct_manager'})
                        action_id = self.env.ref(
                            'hr_holidays.hr_leave_action_action_approve_department').id
                        base_url = self.env[
                            'ir.config_parameter'].sudo().get_param(
                            'web.base.url')
                        ctx = {
                            'url': '%s/web#id=%s&action=%s&model=hr.leave&view_type=form' % (
                                base_url, leave.id, action_id)}
                        self.env.ref(
                            'leave_approver.email_template_send_second_direct_approval').with_context(
                            ctx).send_mail(leave.id)
                        leave_sudo = leave.sudo()
                        partners = []
                        notification_ids = []
                        notification_ids.append((0, 0, {
                            'res_partner_id': leave_sudo.sudo().employee_id.second_direct_manager_id.partner_id.id,
                            'notification_type': 'inbox'}))
                        if leave_sudo.sudo().employee_id.parent_id.user_id.partner_id.id:
                            partners.append(
                                leave_sudo.sudo().employee_id.second_direct_manager_id.partner_id.id)
                        leave_sudo.message_post(partner_ids=partners, body=_(
                            'Dear ' + str(
                                leave.sudo().employee_id.second_direct_manager_id.partner_id.name) + ' Kindly look at ' + (
                                leave_sudo.sudo().employee_id.name) + ' leave.'
                                                                      '<br/><a href=' + ctx.get(
                                'url') + '>Click Here to access'),
                                                subtype='mail.mt_comment',
                                                author_id=leave_sudo.create_uid.partner_id.id,
                                                notification_ids=notification_ids)
                    # Manager
                    elif leave and leave.sudo().employee_id and leave.sudo().employee_id.parent_id.user_id.id:
                        leave.write({'state': 'manager'})
                        action_id = self.env.ref(
                            'hr_holidays.hr_leave_action_action_approve_department').id
                        base_url = self.env[
                            'ir.config_parameter'].sudo().get_param(
                            'web.base.url')
                        ctx = {
                            'url': '%s/web#id=%s&action=%s&model=hr.leave&view_type=form' % (
                                base_url, leave.id, action_id)}
                        self.env.ref(
                            'leave_approver.email_template_send_manager').with_context(
                            ctx).send_mail(leave.id)
                        leave_sudo = leave.sudo()
                        partners = []
                        notification_ids = []
                        notification_ids.append((0, 0, {
                            'res_partner_id': leave_sudo.sudo().employee_id.parent_id.user_id.partner_id.id,
                            'notification_type': 'inbox'}))
                        if leave_sudo.sudo().employee_id.parent_id.user_id.partner_id.id:
                            partners.append(
                                leave_sudo.sudo().employee_id.parent_id.user_id.partner_id.id)
                        leave_sudo.message_post(partner_ids=partners, body=_(
                            'Dear ' + str(
                                leave.sudo().employee_id.parent_id.user_id.partner_id.name) + ' Kindly look at ' + (
                                leave_sudo.sudo().employee_id.name) + ' leave.'
                                                                      '<br/><a href=' + ctx.get(
                                'url') + '>Click Here to access'),
                                                subtype='mail.mt_comment',
                                                author_id=leave_sudo.create_uid.partner_id.id,
                                                notification_ids=notification_ids)
                    # Direct
                    elif leave and leave.employee_id and leave.employee_id.director_id.id:
                        leave.write({'state': 'director'})
                        action_id = self.env.ref(
                            'hr_holidays.hr_leave_action_action_approve_department').id
                        base_url = self.env[
                            'ir.config_parameter'].sudo().get_param(
                            'web.base.url')
                        ctx = {
                            'url': '%s/web#id=%s&action=%s&model=hr.leave&view_type=form' % (
                                base_url, leave.id, action_id)}
                        self.env.ref(
                            'leave_approver.email_template_send_director').with_context(
                            ctx).send_mail(
                            leave.id)
                        leave_sudo = leave.sudo()
                        notification_ids = []
                        notification_ids.append((0, 0, {
                            'res_partner_id': leave_sudo.sudo().employee_id.director_id.partner_id.id,
                            'notification_type': 'inbox'}))
                        partners = []
                        if leave_sudo.sudo().employee_id.director_id.partner_id.id:
                            partners.append(
                                leave_sudo.sudo().employee_id.director_id.partner_id.id)
                        leave_sudo.message_post(partner_ids=partners, body=_(
                            'Dear ' + str(
                                leave.sudo().employee_id.director_id.partner_id.name) + ' Kindly look at ' + (
                                leave_sudo.sudo().employee_id.name) + ' leave.'
                                                                      '<br/><a href=' + ctx.get(
                                'url') + '>Click Here to access'),
                                                subtype='mail.mt_comment',
                                                author_id=leave_sudo.create_uid.partner_id.id,
                                                notification_ids=notification_ids)
                    # HR
                    elif leave and leave.employee_id and leave.employee_id.leave_manager_id.id:
                        leave.write({'state': 'hr'})
                        action_id = self.env.ref(
                            'hr_holidays.hr_leave_action_action_approve_department').id
                        base_url = self.env[
                            'ir.config_parameter'].sudo().get_param(
                            'web.base.url')
                        ctx = {
                            'url': '%s/web#id=%s&action=%s&model=hr.leave&view_type=form' % (
                                base_url, leave.id, action_id)}
                        self.env.ref(
                            'leave_approver.email_template_send_hr_officer').with_context(
                            ctx).send_mail(
                            leave.id)
                        leave_sudo = leave.sudo()
                        notification_ids = []
                        notification_ids.append((0, 0, {
                            'res_partner_id': leave_sudo.sudo().employee_id.leave_manager_id.partner_id.id,
                            'notification_type': 'inbox'}))
                        partners = []
                        if leave_sudo.employee_id.sudo().leave_manager_id.partner_id.id:
                            partners.append(
                                leave_sudo.sudo().employee_id.leave_manager_id.partner_id.id)
                        leave_sudo.message_post(partner_ids=partners, body=_(
                            'Dear ' + str(
                                leave.sudo().employee_id.leave_manager_id.partner_id.name) + ' Kindly look at ' + (
                                leave_sudo.sudo().employee_id.name) + ' leave.'
                                                                      '<br/><a href=' + ctx.get(
                                'url') + '>Click Here to access'),
                                                subtype='mail.mt_comment',
                                                author_id=leave_sudo.create_uid.partner_id.id,
                                                notification_ids=notification_ids)
                    else:
                        leave.action_approve()

            elif self.validation_type == 'direct_manager_and_time_off_officer':
                activity_id = self.env['mail.activity'].search(
                    [('res_id', '=', self.id),
                     ('activity_type_id', '=', self.env.ref(
                         'hr_holidays.mail_act_leave_approval').id)])
                activity_id.action_feedback(feedback="Approved DM")
                note = _("Your have a Time off request to approve")
                self.activity_schedule(
                    'custom_timeoff.mail_act_leave_request_approve_time_off_officer',
                    note=note,
                    user_id=self.holiday_status_id.responsible_id.id or self.env.user.id)
                self.write({'state': 'time_off_officer'})
            #     Create Agenda for time of request.
            if self.employee_id.new_divisions.name == 'Technical':
                reservation_id = self.env['reservation.reason'].search(
                    [('name', '=ilike', self.holiday_status_id.name)],
                    limit=1)
                if reservation_id:
                    self.env['agenda.agenda'].create({
                        'date_start': self.date_from,
                        'date_end': self.date_to,
                        'user_ids': [self.employee_id.user_id.id],
                        'reservation_reason': reservation_id.id,
                    })
                else:
                    reservation_id = self.env['reservation.reason'].create({
                        'name': self.holiday_status_id.name,
                    })
                    self.env['agenda.agenda'].create({
                        'date_start': self.date_from,
                        'date_end': self.date_to,
                        'user_ids': [self.employee_id.user_id.id],
                        'reservation_reason': reservation_id.id,
                    })
        else:
            raise UserError(
                _('Only %s allowed to approve the Request.') % (
                    self.sudo().employee_id.direct_manager_id.name))

    def approve_time_off_officer(self):
        # Check if current user is in responsible_ids
        if self.env.user in self.holiday_status_id.responsible_ids:
            if self.validation_type == 'both':
                self.state = 'validate'
                activity_id = self.env['mail.activity'].search(
                    [('res_id', '=', self.id),
                     ('activity_type_id', '=', self.env.ref(
                         'custom_timeoff.mail_act_leave_request_approve_time_off_officer').id)])
                activity_id.action_feedback(
                    feedback="Approved Time off Officer")

                note = _("Your request for leave is approved")
                self.activity_schedule(
                    'custom_timeoff.mail_act_leave_request_approved',
                    note=note,
                    user_id=self.employee_id.user_id.id
                )
            else:
                activity_id = self.env['mail.activity'].search(
                    [('res_id', '=', self.id),
                     ('activity_type_id', '=', self.env.ref(
                         'custom_timeoff.mail_act_leave_request_approve_time_off_officer').id)])
                activity_id.action_feedback(
                    feedback="Approved Time off Officer")

                self.state = 'validate'
                note = _("Your request for leave is approved")
                self.activity_schedule(
                    'custom_timeoff.mail_act_leave_request_approved',
                    note=note,
                    user_id=self.employee_id.user_id.id
                )

            # Create Agenda from time off requests
            if self.employee_id.new_divisions.name == 'Technical':
                reservation_id = self.env['reservation.reason'].search(
                    [('name', '=ilike', self.holiday_status_id.name)],
                    limit=1
                )
                if reservation_id:
                    agenda = self.env['agenda.agenda'].create({
                        'date_start': self.date_from,
                        'date_end': self.date_to,
                        'user_ids': [self.employee_id.user_id.id],
                        'reservation_reason': reservation_id.id,
                    })
                else:
                    reservation_id = self.env['reservation.reason'].create({
                        'name': self.holiday_status_id.name,
                    })
                    agenda = self.env['agenda.agenda'].create({
                        'date_start': self.date_from,
                        'date_end': self.date_to,
                        'user_ids': [self.employee_id.user_id.id],
                        'reservation_reason': reservation_id.id,
                    })
        else:
            raise UserError(_('Only %s allowed to approve the Request.') % (
                    ', '.join(self.holiday_status_id.responsible_ids.mapped(
                        'name')) or 'Authorized Officers'))
    def approve_time_off_responsible(self):
        if self.env.user.id == self.sudo().employee_id.leave_manager_id.id:
            activity_id = self.env['mail.activity'].search(
                [('res_id', '=', self.id),
                 ('activity_type_id', '=', self.env.ref(
                     'hr_holidays.mail_act_leave_approval').id)])
            activity_id.action_feedback(feedback="Approved DM")
            note = _("Your have a Time off request to approve")
            self.activity_schedule(
                'custom_timeoff.mail_act_leave_request_approve_time_off_officer',
                note=note,
                user_id=self.holiday_status_id.responsible_id.id or self.env.user.id)

            self.write({'state': 'time_off_officer'})
        else:
            raise UserError(
                _('Only %s allowed to approve the Request.') % (
                    self.sudo().employee_id.leave_manager_id.name))

    def manager_approve(self):
        if self.validation_type == 'direct_director':
            for leave in self:
                if leave and leave.sudo().employee_id and leave and leave.sudo().employee_id.parent_id.user_id.id != self.env.user.id:
                    raise ValidationError(
                        _("Only %s can approve leave for employee %s." % (
                            leave.sudo().employee_id.parent_id.user_id.name,
                            leave.sudo().employee_id.name)))
                if leave and leave.sudo().employee_id and leave.sudo().employee_id.director_id.id:
                    leave.write({'state': 'director'})
                    action_id = self.env.ref(
                        'hr_holidays.hr_leave_action_action_approve_department').id
                    base_url = self.env['ir.config_parameter'].sudo().get_param(
                        'web.base.url')
                    ctx = {
                        'url': '%s/web#id=%s&action=%s&model=hr.leave&view_type=form' % (
                        base_url, leave.id, action_id)}
                    self.env.ref(
                        'leave_approver.email_template_send_director').with_context(
                        ctx).send_mail(leave.id)
                    leave_sudo = leave.sudo()
                    notification_ids = []
                    notification_ids.append((0, 0, {
                        'res_partner_id': leave_sudo.sudo().employee_id.director_id.partner_id.id,
                        'notification_type': 'inbox'}))
                    partners = []
                    if leave_sudo.sudo().employee_id.director_id.partner_id.id:
                        partners.append(
                            leave_sudo.sudo().employee_id.director_id.partner_id.id)
                    leave_sudo.message_post(partner_ids=partners, body=_(
                        'Dear ' + str(
                            leave.sudo().employee_id.director_id.partner_id.name) + ' Kindly look at ' + (
                            leave_sudo.sudo().employee_id.name) + ' leave.'
                                                                  '<br/><a href=' + ctx.get(
                            'url') + '>Click Here to access'),
                                            subtype='mail.mt_comment',
                                            author_id=leave_sudo.create_uid.partner_id.id,
                                            notification_ids=notification_ids)
                # HR
                elif leave and leave.sudo().employee_id and leave.sudo().employee_id.leave_manager_id.id:
                    leave.write({'state': 'hr'})
                    action_id = self.env.ref(
                        'hr_holidays.hr_leave_action_action_approve_department').id
                    base_url = self.env['ir.config_parameter'].sudo().get_param(
                        'web.base.url')
                    ctx = {
                        'url': '%s/web#id=%s&action=%s&model=hr.leave&view_type=form' % (
                        base_url, leave.id, action_id)}
                    self.env.ref(
                        'leave_approver.email_template_send_hr_officer').with_context(
                        ctx).send_mail(leave.id)
                    leave_sudo = leave.sudo()
                    notification_ids = []
                    notification_ids.append((0, 0, {
                        'res_partner_id': leave_sudo.sudo().employee_id.leave_manager_id.partner_id.id,
                        'notification_type': 'inbox'}))
                    partners = []
                    if leave_sudo.sudo().employee_id.leave_manager_id.partner_id.id:
                        partners.append(
                            leave_sudo.sudo().employee_id.leave_manager_id.partner_id.id)
                    leave_sudo.message_post(partner_ids=partners, body=_(
                        'Dear ' + str(
                            leave.sudo().employee_id.leave_manager_id.partner_id.name) + ' Kindly look at ' + (
                            leave_sudo.sudo().employee_id.name) + ' leave.'
                                                                  '<br/><a href=' + ctx.get(
                            'url') + '>Click Here to access'),
                                            subtype='mail.mt_comment',
                                            author_id=leave_sudo.create_uid.partner_id.id,
                                            notification_ids=notification_ids)
                else:
                    leave.action_approve()
            # Create Agenda from time off request
            if self.employee_id.new_divisions.name == 'Technical':
                reservation_id = self.env['reservation.reason'].search(
                    [('name', '=ilike', self.holiday_status_id.name)],
                    limit=1)
                if reservation_id:
                    self.env['agenda.agenda'].create({
                        'date_start': self.date_from,
                        'date_end': self.date_to,
                        'user_ids': [self.employee_id.user_id.id],
                        'reservation_reason': reservation_id.id,
                    })
                else:
                    reservation_id = self.env['reservation.reason'].create({
                        'name': self.holiday_status_id.name,
                    })
                    self.env['agenda.agenda'].create({
                        'date_start': self.date_from,
                        'date_end': self.date_to,
                        'user_ids': [self.employee_id.user_id.id],
                        'reservation_reason': reservation_id.id,
                    })
        else:
            activity_id = self.env['mail.activity'].search(
                [('res_id', '=', self.id),
                 ('activity_type_id', '=', self.env.ref(
                     'hr_holidays.mail_act_leave_approval').id)])
            activity_id.action_feedback(feedback="Approved Manager")
            note = _("Your have a Time off request to approve")
            self.activity_schedule(
                'custom_timeoff.mail_act_leave_request_approve_time_off_officer',
                note=note,
                user_id=self.holiday_status_id.sudo().responsible_id.id or self.env.user.id)
            self.write({'state': 'time_off_officer'})
        self.create_agenda()

    def second_direct_manager_approve(self):
        if self.validation_type == 'direct_director':
            for leave in self:
                if leave and leave.employee_id and leave and leave.employee_id.second_direct_manager_id.id != self.env.user.id:
                    raise ValidationError(
                        _("Only %s can approve leave for employee %s." % (
                            leave.employee_id.second_direct_manager_id.name,
                            leave.employee_id.name)))
                if leave and leave.employee_id and leave.employee_id.parent_id.user_id.id:
                    leave.write({'state': 'manager'})
                    action_id = self.env.ref(
                        'hr_holidays.hr_leave_action_action_approve_department').id
                    base_url = self.env['ir.config_parameter'].sudo().get_param(
                        'web.base.url')
                    ctx = {
                        'url': '%s/web#id=%s&action=%s&model=hr.leave&view_type=form' % (
                        base_url, leave.id, action_id)}
                    self.env.ref(
                        'leave_approver.email_template_send_manager').with_context(
                        ctx).send_mail(leave.id)
                    leave_sudo = leave.sudo()
                    partners = []
                    notification_ids = []
                    notification_ids.append((0, 0, {
                        'res_partner_id': leave_sudo.employee_id.parent_id.user_id.partner_id.id,
                        'notification_type': 'inbox'}))
                    if leave_sudo.employee_id.parent_id.user_id.partner_id.id:
                        partners.append(
                            leave_sudo.employee_id.parent_id.user_id.partner_id.id)
                    leave_sudo.message_post(partner_ids=partners, body=_(
                        'Dear ' + str(
                            leave.employee_id.parent_id.user_id.partner_id.name) + ' Kindly look at ' + (
                            leave_sudo.employee_id.name) + ' leave.'
                                                           '<br/><a href=' + ctx.get(
                            'url') + '>Click Here to access'),
                                            subtype='mail.mt_comment',
                                            author_id=leave_sudo.create_uid.partner_id.id,
                                            notification_ids=notification_ids)
                # Direct
                elif leave and leave.employee_id and leave.employee_id.director_id.id:
                    leave.write({'state': 'director'})
                    action_id = self.env.ref(
                        'hr_holidays.hr_leave_action_action_approve_department').id
                    base_url = self.env['ir.config_parameter'].sudo().get_param(
                        'web.base.url')
                    ctx = {
                        'url': '%s/web#id=%s&action=%s&model=hr.leave&view_type=form' % (
                        base_url, leave.id, action_id)}
                    self.env.ref(
                        'leave_approver.email_template_send_director').with_context(
                        ctx).send_mail(leave.id)
                    leave_sudo = leave.sudo()
                    notification_ids = []
                    notification_ids.append((0, 0, {
                        'res_partner_id': leave_sudo.employee_id.director_id.partner_id.id,
                        'notification_type': 'inbox'}))
                    partners = []
                    if leave_sudo.employee_id.director_id.partner_id.id:
                        partners.append(
                            leave_sudo.employee_id.director_id.partner_id.id)
                    leave_sudo.message_post(partner_ids=partners, body=_(
                        'Dear ' + str(
                            leave.employee_id.director_id.partner_id.name) + ' Kindly look at ' + (
                            leave_sudo.employee_id.name) + ' leave.'
                                                           '<br/><a href=' + ctx.get(
                            'url') + '>Click Here to access'),
                                            subtype='mail.mt_comment',
                                            author_id=leave_sudo.create_uid.partner_id.id,
                                            notification_ids=notification_ids)
                # HR
                elif leave and leave.employee_id and leave.employee_id.leave_manager_id.id:
                    leave.write({'state': 'hr'})
                    action_id = self.env.ref(
                        'hr_holidays.hr_leave_action_action_approve_department').id
                    base_url = self.env['ir.config_parameter'].sudo().get_param(
                        'web.base.url')
                    ctx = {
                        'url': '%s/web#id=%s&action=%s&model=hr.leave&view_type=form' % (
                        base_url, leave.id, action_id)}
                    self.env.ref(
                        'leave_approver.email_template_send_hr_officer').with_context(
                        ctx).send_mail(leave.id)
                    leave_sudo = leave.sudo()
                    notification_ids = []
                    notification_ids.append((0, 0, {
                        'res_partner_id': leave_sudo.employee_id.leave_manager_id.partner_id.id,
                        'notification_type': 'inbox'}))
                    partners = []
                    if leave_sudo.employee_id.leave_manager_id.partner_id.id:
                        partners.append(
                            leave_sudo.employee_id.leave_manager_id.partner_id.id)
                    leave_sudo.message_post(partner_ids=partners, body=_(
                        'Dear ' + str(
                            leave.employee_id.leave_manager_id.partner_id.name) + ' Kindly look at ' + (
                            leave_sudo.employee_id.name) + ' leave.'
                                                           '<br/><a href=' + ctx.get(
                            'url') + '>Click Here to access'),
                                            subtype='mail.mt_comment',
                                            author_id=leave_sudo.create_uid.partner_id.id,
                                            notification_ids=notification_ids)
                else:
                    leave.action_approve()

        elif self.validation_type == 'direct_and_second_direct_and_time_off_officer':
            activity_id = self.env['mail.activity'].search(
                [('res_id', '=', self.id),
                 ('activity_type_id', '=', self.env.ref(
                     'custom_timeoff.mail_act_leave_request_approve_second_manager').id)])
            activity_id.action_feedback(
                feedback="Approved Second Direct Manager")
            note = _("Your have a Time off request to approve")
            self.activity_schedule(
                'custom_timeoff.mail_act_leave_request_approve_time_off_officer',
                note=note,
                user_id=self.holiday_status_id.responsible_id.id or self.env.user.id)
            self.write({'state': 'time_off_officer'})

        elif self.validation_type == 'direct_manager_and_second_direct_manager':
            activity_id = self.env['mail.activity'].search(
                [('res_id', '=', self.id),
                 ('activity_type_id', '=', self.env.ref(
                     'custom_timeoff.mail_act_leave_request_approve_second_manager').id)])
            activity_id.action_feedback(
                feedback="Approved Second Direct Manager")
            self.write({'state': 'validate'})
            note = _("Your request for leave is approved")
            self.activity_schedule(
                'custom_timeoff.mail_act_leave_request_approved',
                note=note,
                user_id=self.employee_id.user_id.id)
        self.create_agenda()

    def action_refuse(self):
        current_employee = self.env.user.sudo().employee_id
        if any(holiday.state not in ['draft', 'confirm', 'validate',
                                     'validate1', 'direct_manager',
                                     '2direct_manager',
                                     'manager', 'director', 'hr',
                                     'time_off_officer', 'time_off_responsible']
               for
               holiday in self):
            raise UserError(
                _('Time off request must be confirmed or validated or approval '
                  'stage in order to refuse it.'))

        validated_holidays = self.filtered(lambda hol: hol.state == 'validate1')
        validated_holidays.write(
            {'state': 'refuse', 'first_approver_id': current_employee.id})
        (self - validated_holidays).write(
            {'state': 'refuse', 'second_approver_id': current_employee.id})
        # Delete the meeting
        self.mapped('meeting_id').unlink()
        # If a category that created several holidays, cancel all related
        # linked_requests = self.mapped('linked_request_ids')
        # if linked_requests:
        #     linked_requests.action_refuse()

        # Post a second message, more verbose than the tracking message
        for holiday in self:
            if holiday.sudo().employee_id.user_id:
                holiday.message_post(
                    body=_('Your %s planned on %s has been refused') % (
                        holiday.holiday_status_id.display_name,
                        holiday.date_from),
                    partner_ids=holiday.sudo().employee_id.user_id.partner_id.ids)
        self._remove_resource_leave()
        self.activity_update()
        if self.agenda_id:
            self.agenda_id.sudo().unlink()
        return True

    def _remove_resource_leave(self):
        """
        This method will create entry in resource calendar time off object at the time of holidays cancel/removed
        """
        return self.sudo().env['resource.calendar.leaves'].search(
            [('holiday_id', 'in', self.ids)]).unlink()

    def action_draft(self):
        if any(holiday.state not in ['confirm', 'refuse', 'direct_manager',
                                     'time_off_reponsible'] for holiday in
               self):
            raise UserError(
                _('Time off request state must be "Refused" or "To Approve" in '
                  'order to be reset to draft.'))
        self.write({
            'state': 'draft',
            'first_approver_id': False,
            'second_approver_id': False,
        })
        # linked_requests = self.mapped('linked_request_ids')
        # if linked_requests:
        #     linked_requests.action_draft()
        #     linked_requests.unlink()
        self.activity_update()
        return True

    def action_bypass_approvals(self):
        for rec in self:
            rec.state = 'validate'
            note = _("Your request for leave is approved")
            rec.activity_schedule(
                'custom_timeoff.mail_act_leave_request_approved',
                note=note,
                user_id=rec.employee_id.user_id.id)

    # def action_approve(self, check_state=True):
    #
    #     # Continue normal approval process
    #     if check_state and any(holiday.state != 'confirm' for holiday in self):
    #         raise UserError(
    #             _('Time off request must be confirmed ("To Approve") in order to approve it.')
    #         )
    #
    #     current_employee = self.env.user.employee_id
    #     self.filtered(lambda hol: hol.validation_type == 'both').write(
    #         {'state': 'validate1', 'first_approver_id': current_employee.id}
    #     )
    #
    #     self.filtered(lambda hol: hol.validation_type != 'both').action_validate(check_state)
    #
    #     if not self.env.context.get('leave_fast_create'):
    #         self.activity_update()
    #
    #     note = _("Your request for leave is approved")
    #     self.activity_schedule(
    #         'custom_timeoff.mail_act_leave_request_approved',
    #         note=note,
    #         user_id=self.sudo().employee_id.user_id.id,
    #     )
    #
    #     self.create_agenda()
    #
    #     self.env['mail.message'].create({
    #         'message_type': 'notification',
    #         'subtype_id': self.env.ref('mail.mt_note').id,
    #         'model': 'hr.leave',
    #         'res_id': self.id,
    #         'subject': _('%s will be out of office on %s to %s') % (
    #             self.employee_id.name, self.request_date_from, self.request_date_to),
    #         'body': _('%s will be out of office on %s to %s') % (
    #             self.employee_id.name, self.request_date_from, self.request_date_to),
    #         'partner_ids': [(4, p.partner_id.id) for p in self.employee_id.notified_user_ids],
    #         'notification_ids': [(0, 0, {
    #             'res_partner_id': p.partner_id.id,
    #             'notification_type': 'inbox',
    #             'notification_status': 'sent'
    #         }) for p in self.employee_id.notified_user_ids],
    #     })
    #
    #     return True

    def action_approve(self, check_state=True):
        """
        1. Add direct_director validation exception
        2. Add employee message posting
        3. Add activity scheduling
        4. Add calendar creation
        5. Add team notifications
        """
        # MODIFIED: Add direct_director exception to existing state validation
        # Keep check_state parameter for dashboard redirects, but add director exception
        if check_state and any(
                holiday.validation_type != 'direct_director'
                and holiday.state != 'confirm'
                for holiday in self
        ):
            raise UserError(
                _('Time off request must be confirmed ("To Approve") in order to approve it.')
            )

        # Keep workflow: Two-stage approval
        current_employee = self.env.user.employee_id
        self.filtered(lambda hol: hol.validation_type == 'both').write({
            'state': 'validate1',
            'first_approver_id': current_employee.id
        })

        # ADDED: Post message to employees (from Odoo 13 custom)
        # This is the extra feature - more visible notification
        for holiday in self.filtered(lambda holiday: holiday.sudo().employee_id.user_id):
            holiday.message_post(
                body=_('Your %s planned on %s has been accepted') % (
                    holiday.holiday_status_id.display_name,
                    holiday.date_from
                ),
                partner_ids=holiday.sudo().employee_id.user_id.partner_id.ids
            )

        # Keep Odoo 18 base workflow: Single-stage approval
        self.filtered(lambda hol: hol.validation_type != 'both').action_validate(check_state)

        # Keep Odoo 18 base workflow: Activity cleanup
        if not self.env.context.get('leave_fast_create'):
            self.activity_update()

        # ADDED: Activity scheduling - schedule notification for employee
        note = _("Your request for leave is approved")
        self.activity_schedule(
            'custom_timeoff.mail_act_leave_request_approved',
            note=note,
            user_id=self.sudo().employee_id.user_id.id,
        )

        # ADDED: Calendar creation - create calendar event for approved leave
        self.create_agenda()

        # ADDED: Team notifications - notify team members about out-of-office
        self.env['mail.message'].create({
            'message_type': 'notification',
            'subtype_id': self.env.ref('mail.mt_note').id,
            'model': 'hr.leave',
            'res_id': self.id,
            'subject': _('%s will be out of office on %s to %s') % (
                self.employee_id.name, self.request_date_from, self.request_date_to
            ),
            'body': _('%s will be out of office on %s to %s') % (
                self.employee_id.name, self.request_date_from, self.request_date_to
            ),
            'partner_ids': [(4, p.partner_id.id) for p in self.employee_id.notified_user_ids],
            'notification_ids': [(0, 0, {
                'res_partner_id': p.partner_id.id,
                'notification_type': 'inbox',
                'notification_status': 'sent'
            }) for p in self.employee_id.notified_user_ids],
        })

        return True

    def create_agenda(self):
        """ Method to create agenda from time off requests for the technical employees"""
        if self.employee_id.new_divisions.name == 'Technical':
            reservation_id = self.env['reservation.reason'].sudo().search(
                [('name', '=ilike', self.holiday_status_id.name)],
                limit=1)
            if reservation_id:
                agenda_id = self.env['agenda.agenda'].sudo().create({
                    'date_start': self.date_from,
                    'date_end': self.date_to,
                    'user_ids': [self.employee_id.user_id.id],
                    'reservation_reason': reservation_id.id,
                })
                self.agenda_id = agenda_id.id
            else:
                reservation_id = self.env['reservation.reason'].sudo().create({
                    'name': self.holiday_status_id.name,
                })
                agenda_id = self.env['agenda.agenda'].sudo().create({
                    'date_start': self.date_from,
                    'date_end': self.date_to,
                    'user_ids': [self.employee_id.user_id.id],
                    'reservation_reason': reservation_id.id,
                })
                self.agenda_id = agenda_id.id
