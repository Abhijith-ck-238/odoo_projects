# -*- coding: utf-8 -*-

from odoo import api, fields, models, SUPERUSER_ID, tools
from datetime import datetime, date, timedelta, time
from dateutil import relativedelta
from odoo.exceptions import ValidationError, UserError
from odoo.tools.translate import _
from collections import defaultdict



class HolidaysType(models.Model):
    _inherit = "hr.leave.type"

    leave_validation_type = fields.Selection(selection_add=[('direct_director', 'All approvers')])


class Employee(models.Model):
    _inherit = 'hr.employee'

    direct_manager_id = fields.Many2one('res.users', string='Direct Manager')
    second_direct_manager_id = fields.Many2one('res.users', string='Second Direct Manager')
    director_id = fields.Many2one('res.users', string='Director')
    current_leave_state = fields.Selection(selection_add=[
        ('direct_manager', 'Direct Manager Approval'),
        ('2direct_manager', 'Second Direct Manager Approval'),
        ('manager', 'Manager Approval'),
        ('director', 'Director Approval'),
        ('hr', 'HR Approval'), ])


class EmployeeBase(models.AbstractModel):
    _inherit = 'hr.employee.base'

    direct_manager_id = fields.Many2one('res.users', string='Direct Manager')
    second_direct_manager_id = fields.Many2one('res.users', string='Second Direct Manager')
    director_id = fields.Many2one('res.users', string='Director')
    current_leave_state = fields.Selection(selection_add=[
        ('direct_manager', 'Direct Manager Approval'),
        ('2direct_manager', 'Second Direct Manager Approval'),
        ('manager', 'Manager Approval'),
        ('director', 'Director Approval'),
        ('hr', 'HR Approval'), ])


class EmployeePublic(models.Model):
    _inherit = 'hr.employee.public'

    direct_manager_id = fields.Many2one('res.users', string='Direct Manager')
    second_direct_manager_id = fields.Many2one('res.users', string='Second Direct Manager')
    director_id = fields.Many2one('res.users', string='Director')


class HolidaysRequest(models.Model):
    _inherit = 'hr.leave'

    holiday_type = fields.Selection([
        ('emp', 'By Employee'),
        ('com', 'By Company'),
        ('dep', 'By Department'),
        ('cat', 'By Category')
    ], string='Holiday Type', required=True, default='emp')

    state = fields.Selection([
        ('draft', 'To Submit'),
        ('cancel', 'Cancelled'),  # YTI This state seems to be unused. To remove
        ('confirm', 'To Approve'),
        ('refuse', 'Refused'),
        ('validate1', 'Second Approval'),
        ('direct_manager', 'Direct Manager Approval'),
        ('2direct_manager', 'Second Direct Manager Approval'),
        ('manager', 'Manager Approval'),
        ('director', 'Director Approval'),
        ('hr', 'HR Approval'),
        ('validate', 'Approved')
    ], string='Status', readonly=True, tracking=True, copy=False, default='confirm',
        help="The status is set to 'To Submit', when a time off request is created." +
             "\nThe status is 'To Approve', when time off request is confirmed by user." +
             "\nThe status is 'Refused', when time off request is refused by manager." +
             "\nThe status is 'Approved', when time off request is approved by manager.")

    # ORM Method override
    #
    # @api.onchange('holiday_status_id')
    # def _onchange_holiday_status_id(self):
    #     # res = super(HolidaysRequest, self)._onchange_holiday_status_id()
    #     if self.holiday_status_id and self.holiday_status_id.leave_validation_type == 'direct_director':
    #         # direct manager
    #         if self.employee_id and self.employee_id.direct_manager_id:
    #             self.state = 'direct_manager'
    #         elif self.employee_id and self.employee_id.second_direct_manager_id and not self.employee_id.direct_manager_id:
    #             self.state = '2direct_manager'
    #         elif self.employee_id and self.employee_id.parent_id.user_id and not self.employee_id.second_direct_manager_id and not self.employee_id.direct_manager_id:
    #             self.state = 'manager'
    #         # manager
    #         elif self.employee_id and self.employee_id.director_id and not self.employee_id.parent_id and not self.employee_id.second_direct_manager_id and not self.employee_id.direct_manager_id:
    #             self.state = 'director'
    #         # Director
    #         elif self.employee_id and self.employee_id.leave_manager_id and not self.employee_id.director_id and not self.employee_id.parent_id.user_id and not self.employee_id.second_direct_manager_id and not self.employee_id.direct_manager_id:
    #             self.state = 'hr'
        # return res

    @api.model
    def create(self, vals):
        res = super(HolidaysRequest, self).create(vals)
        leave_sudo = res.sudo()
        partners = []
        if leave_sudo.employee_id.direct_manager_id.partner_id.id:
            partners.append(leave_sudo.employee_id.direct_manager_id.partner_id.id)
        if leave_sudo.employee_id.second_direct_manager_id.partner_id.id:
            partners.append(leave_sudo.employee_id.second_direct_manager_id.partner_id.id)
        if leave_sudo.employee_id.director_id.partner_id.id:
            partners.append(leave_sudo.employee_id.director_id.partner_id.id)
        if leave_sudo.employee_id.parent_id.user_id.partner_id.id:
            partners.append(leave_sudo.employee_id.parent_id.user_id.partner_id.id)
        if leave_sudo.employee_id.leave_manager_id.partner_id.id:
            partners.append(leave_sudo.employee_id.leave_manager_id.partner_id.id)
        leave_sudo.message_subscribe(partner_ids=partners)
        if leave_sudo.employee_id and leave_sudo.holiday_status_id and leave_sudo.holiday_status_id.leave_validation_type == 'direct_director':
            leave_sudo.send_for_approval()
        return res

    def _check_approval_update(self, state):
        """ Check if target state is achievable. """
        if self.env.is_superuser():
            return

        current_employee = self.env.user.employee_id
        is_officer = self.env.user.has_group('hr_holidays.group_hr_holidays_user')
        is_manager = self.env.user.has_group('hr_holidays.group_hr_holidays_manager')

        for holiday in self:
            val_type = holiday.holiday_status_id.leave_validation_type

            if not is_manager and state != 'confirm':
                if state == 'draft':
                    if holiday.state == 'refuse':
                        raise UserError(_('Only a Leave Manager can reset a refused leave.'))
                    if holiday.date_from and holiday.date_from.date() <= fields.Date.today():
                        raise UserError(_('Only a Leave Manager can reset a started leave.'))
                    if holiday.employee_id != current_employee:
                        raise UserError(_('Only a Leave Manager can reset other people leaves.'))
                else:
                    if val_type == 'no_validation' and current_employee == holiday.employee_id:
                        continue
                    # use ir.rule based first access check: department, members, ... (see security.xml)
                    holiday.check_access_rule('write')

                    # This handles states validate1 validate and refuse
                    if holiday.holiday_status_id.leave_validation_type != 'direct_director' and holiday.employee_id == current_employee:
                        raise UserError(_('Only a Leave Manager can approve/refuse its own requests.'))

                    if (state == 'validate1' and val_type == 'both') or (
                            state == 'validate' and val_type == 'manager') and holiday.holiday_type == 'employee':
                        if not is_officer and self.env.user != holiday.employee_id.leave_manager_id:
                            raise UserError(
                                _('You must be either %s\'s manager or Leave manager to approve this leave') % (
                                    holiday.employee_id.name))

    # def _check_validity(self):
    #     sorted_leaves = defaultdict(lambda: self.env['hr.leave'])
    #     for leave in self:
    #         sorted_leaves[(leave.holiday_status_id, leave.date_from.date())] |= leave
    #     for (leave_type, date_from), leaves in sorted_leaves.items():
    #         if leave_type.requires_allocation == 'no':
    #             continue
    #         employees = leaves.employee_id
    #         leave_data = leave_type.get_allocation_data(employees, date_from)
    #         if leave_type.allows_negative:
    #             max_excess = leave_type.max_allowed_negative
    #             for employee in employees:
    #                 if not leave_data[employee]:
    #                     raise ValidationError(_("You do not have any allocation for this time off type.\n"
    #                                             "Please request an allocation before submitting your time off request."))
    #                 if leave_data[employee] and leave_data[employee][0][1]['virtual_remaining_leaves'] < -max_excess:
    #                     raise ValidationError(_("There is no valid allocation to cover that request."))
    #             continue
    #
    #         previous_leave_data = leave_type.with_context(
    #             ignored_leave_ids=leaves.ids
    #         ).get_allocation_data(employees, date_from)
    #         for employee in employees:
    #             previous_emp_data = previous_leave_data[employee] and previous_leave_data[employee][0][1]['virtual_excess_data']
    #             emp_data = leave_data[employee] and leave_data[employee][0][1]['virtual_excess_data']
    #             if not leave_data[employee]:
    #                 raise ValidationError(_("You do not have any allocation for this time off type.\n"
    #                                         "Please request an allocation before submitting your time off request."))
    #             if not previous_emp_data and not emp_data:
    #                 continue
    #             if previous_emp_data != emp_data and len(emp_data) >= len(previous_emp_data):
    #                 raise ValidationError(_("There is no valid allocation to cover that request."))

    def action_validate(self, check_state=True):
        current_employee = self.env.user.employee_id
        if any(holiday.holiday_status_id.leave_validation_type != 'direct_director' and holiday.state not in ['confirm',
                                                                                                              'validate1']
               for holiday in self):
            raise UserError(_('Time off request must be confirmed in order to approve it.'))

        self.write({'state': 'validate'})
        self.filtered(lambda holiday: holiday.holiday_status_id.leave_validation_type == 'both').write(
            {'second_approver_id': current_employee.id})
        self.filtered(lambda holiday: holiday.holiday_status_id.leave_validation_type != 'both').write(
            {'first_approver_id': current_employee.id})

        for holiday in self.filtered(lambda holiday: holiday.holiday_type != 'emp'):
            if holiday.holiday_type == 'cat':
                employees = holiday.category_id.employee_ids
            elif holiday.holiday_type == 'com':
                employees = self.env['hr.employee'].search([('company_id', '=', holiday.mode_company_id.id)])
            else:
                employees = holiday.department_id.member_ids

            conflicting_leaves = self.env['hr.leave'].with_context(
                tracking_disable=True,
                mail_activity_automation_skip=True,
                leave_fast_create=True
            ).search([
                ('date_from', '<=', holiday.date_to),
                ('date_to', '>', holiday.date_from),
                ('state', 'not in', ['cancel', 'refuse']),
                ('holiday_type', '=', 'employee'),
                ('employee_id', 'in', employees.ids)])

            if conflicting_leaves:
                # YTI: More complex use cases could be managed in master
                if holiday.leave_type_request_unit != 'day' or any(
                        l.leave_type_request_unit == 'hour' for l in conflicting_leaves):
                    raise ValidationError(_('You can not have 2 leaves that overlaps on the same day.'))

                # keep track of conflicting leaves states before refusal
                target_states = {l.id: l.state for l in conflicting_leaves}
                conflicting_leaves.action_refuse()
                split_leaves_vals = []
                for conflicting_leave in conflicting_leaves:
                    if conflicting_leave.leave_type_request_unit == 'half_day' and conflicting_leave.request_unit_half:
                        continue

                    # Leaves in days
                    if conflicting_leave.date_from < holiday.date_from:
                        before_leave_vals = conflicting_leave.copy_data({
                            'date_from': conflicting_leave.date_from.date(),
                            'date_to': holiday.date_from.date() + timedelta(days=-1),
                            'state': target_states[conflicting_leave.id],
                        })[0]
                        before_leave = self.env['hr.leave'].new(before_leave_vals)
                        before_leave._onchange_request_parameters()
                        # Could happen for part-time contract, that time off is not necessary
                        # anymore.
                        # Imagine you work on monday-wednesday-friday only.
                        # You take a time off on friday.
                        # We create a company time off on friday.
                        # By looking at the last attendance before the company time off
                        # start date to compute the date_to, you would have a date_from > date_to.
                        # Just don't create the leave at that time. That's the reason why we use
                        # new instead of create. As the leave is not actually created yet, the sql
                        # constraint didn't check date_from < date_to yet.
                        if before_leave.date_from < before_leave.date_to:
                            split_leaves_vals.append(before_leave._convert_to_write(before_leave._cache))
                    if conflicting_leave.date_to > holiday.date_to:
                        after_leave_vals = conflicting_leave.copy_data({
                            'date_from': holiday.date_to.date() + timedelta(days=1),
                            'date_to': conflicting_leave.date_to.date(),
                            'state': target_states[conflicting_leave.id],
                        })[0]
                        after_leave = self.env['hr.leave'].new(after_leave_vals)
                        after_leave._onchange_request_parameters()
                        # Could happen for part-time contract, that time off is not necessary
                        # anymore.
                        if after_leave.date_from < after_leave.date_to:
                            split_leaves_vals.append(after_leave._convert_to_write(after_leave._cache))

                split_leaves = self.env['hr.leave'].with_context(
                    tracking_disable=True,
                    mail_activity_automation_skip=True,
                    leave_fast_create=True,
                    leave_skip_state_check=True
                ).create(split_leaves_vals)

                split_leaves.filtered(lambda l: l.state in 'validate')._validate_leave_request()

            values = holiday._prepare_employees_holiday_values(employees)
            leaves = self.env['hr.leave'].with_context(
                tracking_disable=True,
                mail_activity_automation_skip=True,
                leave_fast_create=True,
                leave_skip_state_check=True,
            ).create(values)

            leaves._validate_leave_request()

        employee_requests = self.filtered(lambda hol: hol.holiday_type == 'employee')
        employee_requests._validate_leave_request()
        if not self.env.context.get('leave_fast_create'):
            employee_requests.filtered(
                lambda holiday: holiday.leave_validation_type != 'no_validation').activity_update()
        return True

    def action_approve(self):
        # if validation_type == 'both': this method is the first approval approval
        # if validation_type != 'both': this method calls action_validate() below
        if any(holiday.holiday_status_id.leave_validation_type != 'direct_director' and holiday.state != 'confirm' for
               holiday in self):
            raise UserError(_('Time off request must be confirmed ("To Approve") in order to approve it.'))

        current_employee = self.env.user.employee_id
        self.filtered(lambda hol: hol.holiday_status_id.leave_validation_type == 'both').write(
            {'state': 'validate1', 'first_approver_id': current_employee.id})

        # Post a second message, more verbose than the tracking message
        for holiday in self.filtered(lambda holiday: holiday.employee_id.user_id):
            holiday.message_post(
                body=_('Your %s planned on %s has been accepted' % (
                    holiday.holiday_status_id.display_name, holiday.date_from)),
                partner_ids=holiday.employee_id.user_id.partner_id.ids)

        self.filtered(lambda hol: not hol.holiday_status_id.leave_validation_type == 'both').action_validate()
        if not self.env.context.get('leave_fast_create'):
            self.activity_update()
        return True

    def action_refuse(self):
        current_employee = self.env.user.employee_id
        if any(holiday.state not in ['draft', 'confirm', 'validate', 'validate1', 'direct_manager', '2direct_manager',
                                     'manager', 'director', 'hr'] for holiday in self):
            raise UserError(
                _('Time off request must be confirmed or validated or approval stage in order to refuse it.'))

        validated_holidays = self.filtered(lambda hol: hol.state == 'validate1')
        validated_holidays.write({'state': 'refuse', 'first_approver_id': current_employee.id})
        (self - validated_holidays).write({'state': 'refuse', 'second_approver_id': current_employee.id})
        # Delete the meeting
        # self.mapped('meeting_id').unlink()
        # If a category that created several holidays, cancel all related
        # linked_requests = self.mapped('linked_request_ids')
        # if linked_requests:
        #     linked_requests.action_refuse()

        # Post a second message, more verbose than the tracking message
        for holiday in self:
            if holiday.employee_id.user_id:
                holiday.message_post(
                    body=_('Your %s planned on %s has been refused') % (
                        holiday.holiday_status_id.display_name, holiday.date_from),
                    partner_ids=holiday.employee_id.user_id.partner_id.ids)

        self._remove_resource_leave()
        self.activity_update()
        return True

    def send_leave(self, params):
        for leave in self:
            if len(params) == 4:
                leave_sudo = leave.sudo()

                ctx = dict(leave._context)

                state_to_write = ctx.get('send_to')

                partners = params[0]

                partner_id = params[1]
                template = params[2]
                notification_ids = params[3]
                leave.write({'state': state_to_write})
                template.with_context(ctx).send_mail(leave.id)
                leave_sudo.message_post(
                    partner_ids=[partners],
                    body=_("Dear %s ,"
                           "Kindly look at %s leave %s "
                           "click here to access", partner_id.name, leave_sudo.employee_id.name, ctx.get('url')),
                    subtype_xmlid='mail.mt_comment',
                    author_id=leave_sudo.create_uid.partner_id.id)
            return True

    def send_for_approval(self):
        for leave in self:
            ctx = dict(leave._context)
            action_id = self.env.ref('hr_holidays.hr_leave_action_action_approve_department').id
            base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
            ctx.update(
                {'url': '%s/web#id=%s&action=%s&model=hr.leave&view_type=form' % (base_url, leave.id, action_id)})
            approvers = []
            if leave.holiday_status_id and leave.holiday_status_id.leave_validation_type == 'direct_director':
                # direct manager
                if leave.employee_id and leave.employee_id.direct_manager_id:
                    ctx.update(send_to='direct_manager')
                    approvers.append(leave.employee_id.direct_manager_id.id)
                elif leave.employee_id and leave.employee_id.second_direct_manager_id and not leave.employee_id.direct_manager_id:
                    ctx.update(send_to='2direct_manager')
                    approvers.append(leave.employee_id.second_direct_manager_id.id)
                    # raise ValidationError(_("Direct manager not set in employee %s." %(leave.employee_id.name)))
                elif leave.employee_id and leave.employee_id.parent_id.user_id and not leave.employee_id.second_direct_manager_id and not leave.employee_id.direct_manager_id:
                    ctx.update(send_to='manager')
                    approvers.append(leave.employee_id.parent_id.user_id.id)
                    # raise ValidationError(_("Second Direct manager not set in employee %s." %(leave.employee_id.name)))
                # manager
                elif leave.employee_id and leave.employee_id.director_id and not leave.employee_id.parent_id and not leave.employee_id.second_direct_manager_id and not leave.employee_id.direct_manager_id:
                    ctx.update(send_to='director')
                    approvers.append(leave.employee_id.director_id.id)
                    # raise ValidationError(_("Manager not set in employee %s." %(leave.employee_id.name)))
                # Director
                elif leave.employee_id and leave.employee_id.leave_manager_id and not leave.employee_id.director_id and not leave.employee_id.parent_id.user_id and not leave.employee_id.second_direct_manager_id and not leave.employee_id.direct_manager_id:
                    ctx.update(send_to='hr')
                    approvers.append(leave.employee_id.leave_manager_id.id)
                    # raise ValidationError(_("Director  not set in employee %s." %(leave.employee_id.name)))
                # HR Officer
                if len(approvers) == 0:
                    raise ValidationError(
                        _("There has to be at least HR approver in employee %s." % (leave.employee_id.name)))
            leave_sudo = leave.sudo()
            params = []

            params_dict = {}
            notification_ids = []
            if ctx.get('send_to') and ctx.get('send_to') == 'direct_manager':
                # direct_manager
                partner_id = leave_sudo.employee_id.direct_manager_id.partner_id.id
                email_temp = self.env.ref('leave_approver.email_template_send_direct_approval')

                notification_ids.append((0, 0, {
                    'res_partner_id': leave_sudo.employee_id.direct_manager_id.partner_id.id,
                    'notification_type': 'inbox'}))

                params.append(partner_id)
                params.append(leave_sudo.employee_id.direct_manager_id.partner_id)
                params.append(email_temp)
                params.append(notification_ids)

            if ctx.get('send_to') and ctx.get('send_to') == '2direct_manager':
                # 2direct_manager
                partner_id = leave_sudo.employee_id.second_direct_manager_id.partner_id.id
                email_temp = self.env.ref('leave_approver.email_template_send_second_direct_approval')
                notification_ids.append((0, 0, {
                    'res_partner_id': leave_sudo.employee_id.second_direct_manager_id.partner_id.id,
                    'notification_type': 'inbox'}))
                params.append(partner_id)
                params.append(leave_sudo.employee_id.second_direct_manager_id.partner_id)
                params.append(email_temp)
                params.append(notification_ids)

            if ctx.get('send_to') and ctx.get('send_to') == 'manager':
                # manager
                partner_id = leave_sudo.employee_id.parent_id.user_id.partner_id.id
                email_temp = self.env.ref('leave_approver.email_template_send_manager')
                notification_ids.append((0, 0, {
                    'res_partner_id': leave_sudo.employee_id.parent_id.user_id.partner_id.id,
                    'notification_type': 'inbox'}))
                params.append(partner_id)
                params.append(leave_sudo.employee_id.parent_id.user_id.partner_id)
                params.append(email_temp)
                params.append(notification_ids)
            if ctx.get('send_to') and ctx.get('send_to') == 'director':
                # dirctor
                partner_id = leave_sudo.employee_id.director_id.partner_id.id
                email_temp = self.env.ref('leave_approver.email_template_send_director')
                notification_ids.append((0, 0, {
                    'res_partner_id': leave_sudo.employee_id.director_id.partner_id.id,
                    'notification_type': 'inbox'}))
                params.append(partner_id)
                params.append(leave_sudo.employee_id.director_id.partner_id)
                params.append(email_temp)
                params.append(notification_ids)
            if ctx.get('send_to') and ctx.get('send_to') == 'hr':
                # hr
                partner_id = leave_sudo.employee_id.leave_manager_id.partner_id.id
                email_temp = self.env.ref('leave_approver.email_template_send_hr_officer')
                notification_ids.append((0, 0, {
                    'res_partner_id': leave_sudo.employee_id.leave_manager_id.partner_id.id,
                    'notification_type': 'inbox'}))
                params.append(partner_id)
                params.append(leave_sudo.employee_id.leave_manager_id.partner_id)
                params.append(email_temp)
                params.append(notification_ids)
            if leave.number_of_days <= 7:
                leave.with_context(ctx).send_leave(params)
            else:
                date1 = datetime.strptime(str(leave.create_date.date()), '%Y-%m-%d').date()
                date2 = leave.request_date_from
                delta = date2 - date1
                if delta.days > 60:
                    leave.with_context(ctx).send_leave(params)
                else:
                    raise ValidationError(_("You can apply for leave more then 7 days 2 months before only."))

    def direct_manager_approve(self):
        for leave in self:
            if leave and leave.employee_id and leave.employee_id.direct_manager_id.id and leave.employee_id.direct_manager_id.id != self.env.user.id:
                raise ValidationError(_("Only %s can approve leave for employee %s." % (
                    leave.employee_id.direct_manager_id.name, leave.employee_id.name)))
            # Second Direct manager
            if leave and leave.employee_id and leave and leave.employee_id.second_direct_manager_id.id:
                leave.write({'state': '2direct_manager'})
                action_id = self.env.ref('hr_holidays.hr_leave_action_action_approve_department').id
                base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
                ctx = {'url': '%s/web#id=%s&action=%s&model=hr.leave&view_type=form' % (base_url, leave.id, action_id)}
                self.env.ref('leave_approver.email_template_send_second_direct_approval').with_context(ctx).send_mail(
                    leave.id)
                leave_sudo = leave.sudo()
                partners = []
                notification_ids = []
                notification_ids.append((0, 0, {
                    'res_partner_id': leave_sudo.employee_id.second_direct_manager_id.partner_id.id,
                    'notification_type': 'inbox'}))
                if leave_sudo.employee_id.parent_id.user_id.partner_id.id:
                    partners.append(leave_sudo.employee_id.second_direct_manager_id.partner_id.id)
                leave_sudo.message_post(
                    partner_ids=partners,
                    body=_("Dear %s ,"
                           "Kindly look at %s leave %s "
                           "click here to access", str(leave.employee_id.second_direct_manager_id.partner_id.name),
                           leave_sudo.employee_id.name, ctx.get('url')),
                    subtype_xmlid='mail.mt_comment',
                    author_id=leave_sudo.create_uid.partner_id.id,
                    notification_ids=notification_ids)
            # Manager
            elif leave and leave.employee_id and leave.employee_id.parent_id.user_id.id:
                leave.write({'state': 'manager'})
                action_id = self.env.ref('hr_holidays.hr_leave_action_action_approve_department').id
                base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
                ctx = {'url': '%s/web#id=%s&action=%s&model=hr.leave&view_type=form' % (base_url, leave.id, action_id)}
                self.env.ref('leave_approver.email_template_send_manager').with_context(ctx).send_mail(leave.id)
                leave_sudo = leave.sudo()
                partners = []
                notification_ids = []
                notification_ids.append((0, 0, {
                    'res_partner_id': leave_sudo.employee_id.parent_id.user_id.partner_id.id,
                    'notification_type': 'inbox'}))
                if leave_sudo.employee_id.parent_id.user_id.partner_id.id:
                    partners.append(leave_sudo.employee_id.parent_id.user_id.partner_id.id)
                leave_sudo.message_post(
                    partner_ids=partners,
                    body=_("Dear %s ,"
                           "Kindly look at %s leave %s "
                           "click here to access", str(leave.employee_id.parent_id.user_id.partner_id.name),
                           leave_sudo.employee_id.name, ctx.get('url')),
                    subtype_xmlid='mail.mt_comment',
                    author_id=leave_sudo.create_uid.partner_id.id,
                )
            # Direct
            elif leave and leave.employee_id and leave.employee_id.director_id.id:
                leave.write({'state': 'director'})
                action_id = self.env.ref('hr_holidays.hr_leave_action_action_approve_department').id
                base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
                ctx = {'url': '%s/web#id=%s&action=%s&model=hr.leave&view_type=form' % (base_url, leave.id, action_id)}
                self.env.ref('leave_approver.email_template_send_director').with_context(ctx).send_mail(leave.id)
                leave_sudo = leave.sudo()
                notification_ids = []
                notification_ids.append((0, 0, {
                    'res_partner_id': leave_sudo.employee_id.director_id.partner_id.id,
                    'notification_type': 'inbox'}))
                partners = []
                if leave_sudo.employee_id.director_id.partner_id.id:
                    partners.append(leave_sudo.employee_id.director_id.partner_id.id)
                leave_sudo.message_post(
                    partner_ids=partners,
                    body=_("Dear %s ,"
                           "Kindly look at %s leave %s "
                           "click here to access", str(leave.employee_id.director_id.partner_id.name),
                           leave_sudo.employee_id.name, ctx.get('url')),
                    subtype_xmlid='mail.mt_comment',
                    author_id=leave_sudo.create_uid.partner_id.id,
                )
            # HR
            elif leave and leave.employee_id and leave.employee_id.leave_manager_id.id:
                leave.write({'state': 'hr'})
                action_id = self.env.ref('hr_holidays.hr_leave_action_action_approve_department').id
                base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
                ctx = {'url': '%s/web#id=%s&action=%s&model=hr.leave&view_type=form' % (base_url, leave.id, action_id)}
                self.env.ref('leave_approver.email_template_send_hr_officer').with_context(ctx).send_mail(leave.id)
                leave_sudo = leave.sudo()
                notification_ids = []
                notification_ids.append((0, 0, {
                    'res_partner_id': leave_sudo.employee_id.leave_manager_id.partner_id.id,
                    'notification_type': 'inbox'}))
                partners = []
                if leave_sudo.employee_id.leave_manager_id.partner_id.id:
                    partners.append(leave_sudo.employee_id.leave_manager_id.partner_id.id)
                leave_sudo.message_post(
                    partner_ids=partners,
                    body=_("Dear %s ,"
                           "Kindly look at %s leave %s "
                           "click here to access", str(leave.employee_id.leave_manager_id.partner_id.name),
                           leave_sudo.employee_id.name, ctx.get('url')),
                    subtype_xmlid='mail.mt_comment',
                    author_id=leave_sudo.create_uid.partner_id.id,
                )
            else:
                leave.action_approve()

    def second_direct_manager_approve(self):
        for leave in self:
            if leave and leave.employee_id and leave and leave.employee_id.second_direct_manager_id.id != self.env.user.id:
                raise ValidationError(_("Only %s can approve leave for employee %s." % (
                    leave.employee_id.second_direct_manager_id.name, leave.employee_id.name)))
            if leave and leave.employee_id and leave.employee_id.parent_id.user_id.id:
                leave.write({'state': 'manager'})
                action_id = self.env.ref('hr_holidays.hr_leave_action_action_approve_department').id
                base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
                ctx = {'url': '%s/web#id=%s&action=%s&model=hr.leave&view_type=form' % (base_url, leave.id, action_id)}
                self.env.ref('leave_approver.email_template_send_manager').with_context(ctx).send_mail(leave.id)
                leave_sudo = leave.sudo()
                partners = []
                notification_ids = []
                notification_ids.append((0, 0, {
                    'res_partner_id': leave_sudo.employee_id.parent_id.user_id.partner_id.id,
                    'notification_type': 'inbox'}))
                if leave_sudo.employee_id.parent_id.user_id.partner_id.id:
                    partners.append(leave_sudo.employee_id.parent_id.user_id.partner_id.id)
                leave_sudo.message_post(
                    partner_ids=partners,
                    body=_("Dear %s ,"
                           "Kindly look at %s leave %s "
                           "click here to access", str(leave.employee_id.parent_id.user_id.partner_id.name),
                           leave_sudo.employee_id.name, ctx.get('url')),

                    subtype_xmlid='mail.mt_comment',
                    author_id=leave_sudo.create_uid.partner_id.id,
                )
            # Direct
            elif leave and leave.employee_id and leave.employee_id.director_id.id:
                leave.write({'state': 'director'})
                action_id = self.env.ref('hr_holidays.hr_leave_action_action_approve_department').id
                base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
                ctx = {'url': '%s/web#id=%s&action=%s&model=hr.leave&view_type=form' % (base_url, leave.id, action_id)}
                self.env.ref('leave_approver.email_template_send_director').with_context(ctx).send_mail(leave.id)
                leave_sudo = leave.sudo()
                notification_ids = []
                notification_ids.append((0, 0, {
                    'res_partner_id': leave_sudo.employee_id.director_id.partner_id.id,
                    'notification_type': 'inbox'}))
                partners = []
                if leave_sudo.employee_id.director_id.partner_id.id:
                    partners.append(leave_sudo.employee_id.director_id.partner_id.id)
                leave_sudo.message_post(
                    partner_ids=partners,
                    body=_("Dear %s ,"
                           "Kindly look at %s leave %s "
                           "click here to access", str(leave.employee_id.director_id.partner_id.name),
                           leave_sudo.employee_id.name, ctx.get('url')),

                    subtype_xmlid='mail.mt_comment',
                    author_id=leave_sudo.create_uid.partner_id.id,
                )
            # HR
            elif leave and leave.employee_id and leave.employee_id.leave_manager_id.id:
                leave.write({'state': 'hr'})
                action_id = self.env.ref('hr_holidays.hr_leave_action_action_approve_department').id
                base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
                ctx = {'url': '%s/web#id=%s&action=%s&model=hr.leave&view_type=form' % (base_url, leave.id, action_id)}
                self.env.ref('leave_approver.email_template_send_hr_officer').with_context(ctx).send_mail(leave.id)
                leave_sudo = leave.sudo()
                notification_ids = []
                notification_ids.append((0, 0, {
                    'res_partner_id': leave_sudo.employee_id.leave_manager_id.partner_id.id,
                    'notification_type': 'inbox'}))
                partners = []
                if leave_sudo.employee_id.leave_manager_id.partner_id.id:
                    partners.append(leave_sudo.employee_id.leave_manager_id.partner_id.id)
                leave_sudo.message_post(
                    partner_ids=partners,
                    body=_("Dear %s ,"
                           "Kindly look at %s leave %s "
                           "click here to access", str(leave.employee_id.leave_manager_id.partner_id.name),
                           leave_sudo.employee_id.name, ctx.get('url')),

                    subtype_xmlid='mail.mt_comment',
                    author_id=leave_sudo.create_uid.partner_id.id,
                )
            else:
                leave.action_approve()

    def manager_approve(self):
        for leave in self:
            if leave and leave.employee_id and leave and leave.employee_id.parent_id.user_id.id != self.env.user.id:
                raise ValidationError(_("Only %s can approve leave for employee %s." % (
                    leave.employee_id.parent_id.user_id.name, leave.employee_id.name)))
            if leave and leave.employee_id and leave.employee_id.director_id.id:
                leave.write({'state': 'director'})
                action_id = self.env.ref('hr_holidays.hr_leave_action_action_approve_department').id
                base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
                ctx = {'url': '%s/web#id=%s&action=%s&model=hr.leave&view_type=form' % (base_url, leave.id, action_id)}
                self.env.ref('leave_approver.email_template_send_director').with_context(ctx).send_mail(leave.id)
                leave_sudo = leave.sudo()
                notification_ids = []
                notification_ids.append((0, 0, {
                    'res_partner_id': leave_sudo.employee_id.director_id.partner_id.id,
                    'notification_type': 'inbox'}))
                partners = []
                if leave_sudo.employee_id.director_id.partner_id.id:
                    partners.append(leave_sudo.employee_id.director_id.partner_id.id)
                leave_sudo.message_post(
                    partner_ids=partners,
                    body=_("Dear %s ,"
                           "Kindly look at %s leave %s "
                           "click here to access", str(leave.employee_id.director_id.partner_id.name),
                           leave_sudo.employee_id.name, ctx.get('url')),
                    subtype_xmlid='mail.mt_comment',
                    author_id=leave_sudo.create_uid.partner_id.id,
                )
            # HR
            elif leave and leave.employee_id and leave.employee_id.leave_manager_id.id:
                leave.write({'state': 'hr'})
                action_id = self.env.ref('hr_holidays.hr_leave_action_action_approve_department').id
                base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
                ctx = {'url': '%s/web#id=%s&action=%s&model=hr.leave&view_type=form' % (base_url, leave.id, action_id)}
                self.env.ref('leave_approver.email_template_send_hr_officer').with_context(ctx).send_mail(leave.id)
                leave_sudo = leave.sudo()
                notification_ids = []
                notification_ids.append((0, 0, {
                    'res_partner_id': leave_sudo.employee_id.leave_manager_id.partner_id.id,
                    'notification_type': 'inbox'}))
                partners = []
                if leave_sudo.employee_id.leave_manager_id.partner_id.id:
                    partners.append(leave_sudo.employee_id.leave_manager_id.partner_id.id)
                leave_sudo.message_post(
                    partner_ids=partners,
                    body=_("Dear %s ,"
                           "Kindly look at %s leave %s "
                           "click here to access", str(leave.employee_id.leave_manager_id.partner_id.name),
                           leave_sudo.employee_id.name, ctx.get('url')),
                    subtype_xmlid='mail.mt_comment',
                    author_id=leave_sudo.create_uid.partner_id.id,
                )
            else:
                leave.action_approve()

    def director_approve(self):
        for leave in self:
            if leave and leave.employee_id and leave and leave.employee_id.director_id.id != self.env.user.id:
                raise ValidationError(_("Only %s can approve leave for employee %s." % (
                    leave.employee_id.director_id.name, leave.employee_id.name)))
            if leave and leave.employee_id and leave.employee_id.leave_manager_id.id:
                leave.write({'state': 'hr'})
                action_id = self.env.ref('hr_holidays.hr_leave_action_action_approve_department').id
                base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
                ctx = {'url': '%s/web#id=%s&action=%s&model=hr.leave&view_type=form' % (base_url, leave.id, action_id)}
                self.env.ref('leave_approver.email_template_send_hr_officer').with_context(ctx).send_mail(leave.id)
                leave_sudo = leave.sudo()
                notification_ids = []
                notification_ids.append((0, 0, {
                    'res_partner_id': leave_sudo.employee_id.leave_manager_id.partner_id.id,
                    'notification_type': 'inbox'}))
                partners = []
                if leave_sudo.employee_id.leave_manager_id.partner_id.id:
                    partners.append(leave_sudo.employee_id.leave_manager_id.partner_id.id)
                leave_sudo.message_post(
                    partner_ids=partners,
                    body=_("Dear %s ,"
                           "Kindly look at %s leave %s "
                           "click here to access", str(leave.employee_id.leave_manager_id.partner_id.name),
                           leave_sudo.employee_id.name, ctx.get('url')),
                    subtype_xmlid='mail.mt_comment',
                    author_id=leave_sudo.create_uid.partner_id.id,
                )
            else:
                leave.action_approve()

    def hr_officer_approve(self):
        for leave in self:
            if leave and leave.employee_id and leave and leave.employee_id.leave_manager_id.id != self.env.user.id:
                raise ValidationError(_("Only %s can approve leave for employee %s." % (
                    leave.employee_id.leave_manager_id.name, leave.employee_id.name)))
            leave.action_approve()
