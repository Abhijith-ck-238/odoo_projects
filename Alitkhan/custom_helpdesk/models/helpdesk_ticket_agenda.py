import calendar
from datetime import timedelta, datetime

from odoo import models, fields, api
from odoo.tools import date_utils


class Agenda(models.Model):
    """ Agenda """
    _name = 'agenda.agenda'
    _rec_name = 'reservation_reason'

    @api.model
    def default_get(self, fields_list):
        result = super().default_get(fields_list)
        if 'date_start' in fields_list and 'date_start' not in result:
            now = fields.Datetime.now()
            # Round the datetime to the nearest half hour (e.g. 08:17 => 08:30 and 08:37 => 09:00)
            result['date_start'] = now.replace(second=0, microsecond=0) + timedelta(minutes=-now.minute % 30)
        if 'date_end' in fields_list and 'date_end' not in result and result.get('date_start'):
            result['date_end'] = result['date_start'] + timedelta(days=1)
        return result

    user_ids = fields.Many2many('res.users', string="Users")
    user_id_custom = fields.Char(string='Users', compute='_get_users',
                                 store=True)
    date_start = fields.Datetime(string="Starting Date",
                                 compute='compute_task_range', store=True,
                                 readonly=False)
    date_end = fields.Datetime(string="Ending Date",
                               compute='compute_task_range', store=True,
                               readonly=False)
    reservation_reason = fields.Many2one('reservation.reason',
                                         string="Reservation Reason")
    task_id = fields.Many2one('project.task', string="Task", ondelete='cascade')
    is_conflicted = fields.Boolean(string="Check conflicting Agenda's")
    available_user_ids = fields.One2many('available.resource', 'agenda_id',
                                         string="Available Resources",
                                         compute='compute_available_users',
                                         store=True)
    helpdesk_ticket_id = fields.Many2one('helpdesk.ticket',
                                         related='task_id.related_helpdesk_ticket')
    province_id = fields.Many2one('contract.province',
                                  related='helpdesk_ticket_id.province_id')
    vehicle_ids = fields.Many2many('fleet.vehicle',
                                   related='task_id.vehicle_ids')
    description = fields.Text(related='helpdesk_ticket_id.description')
    user_names = fields.Text(compute='compute_user_names')
    vehicle_names = fields.Text(compute='compute_vehicle_names')
    active = fields.Boolean(string="Active", default=True,
                            compute='compute_agenda_active', store=True)
    has_friday = fields.Boolean(string="Has Friday",
                                compute='compute_has_friday',
                                search="search_friday_jobs", default=False
                                )
    is_this_month_job = fields.Boolean(string="Is this month job", default=False, compute='compute_is_this_month_job',
                                       search="search_is_this_month_job")
    x_studio_stage = fields.Many2one('helpdesk.stage', string="Helpdesk Stage")


    @api.depends('date_start', 'date_end')
    def compute_is_this_month_job(self):
        for agenda in self:
            date = fields.date.today()
            start_date = datetime(date.year, date.month, 1)
            end_date = datetime(date.year, date.month, calendar.mdays[date.month])
            previous_month = date_utils.subtract(date, months=1)
            starting_prevs_month = date_utils.start_of(previous_month, "month")
            ending_prevs_month = date_utils.end_of(previous_month, "month")
            next_month = date_utils.add(date, months=1)
            starting_next_month = date_utils.start_of(next_month, "month")
            ending_next_month = date_utils.end_of(next_month, "month")
            if agenda.date_start and agenda.date_end:
                if ((agenda.date_start.date() >= start_date.date() and agenda.date_start.date() <= end_date.date()) or (
                        agenda.date_start.date() >= starting_prevs_month and agenda.date_start.date() <= ending_prevs_month)) and (
                        (agenda.date_end.date() >= start_date.date() and agenda.date_end.date() <= end_date.date()) or (
                        agenda.date_end.date() >= starting_next_month and agenda.date_end.date() <= ending_next_month)):
                    agenda.is_this_month_job = True
                else:
                    agenda.is_this_month_job = False
            else:
                agenda.is_this_month_job = False

    @api.depends('date_start', 'date_end')
    def compute_has_friday(self):
        """ Method to compute friday jobs."""
        for rec in self:
            start_date = rec.date_start  # YYYY, MM, DD format
            end_date = rec.date_end
            day_to_find = 4  # 0 = Monday, 1 = Tuesday, ..., 6 = Sunday
            delta = timedelta(days=1)
            current_date = start_date
            if current_date:
                while current_date <= end_date:
                    if current_date.weekday() == day_to_find:
                        rec.has_friday = True
                        break
                    else:
                        rec.has_friday = False
                    current_date += delta
            else:
                rec.has_friday = False

    def search_friday_jobs(self, operator, value):
        """ Method to search friday jobs."""
        if operator == '=':
            agenda_ids = self.env['agenda.agenda'].search([])
            res = agenda_ids.filtered(
                lambda rec: rec.has_friday)

            return [('id', 'in', res.ids)]
        if operator == '!=':
            agenda_ids = self.env['agenda.agenda'].search([])
            res = agenda_ids.filtered(
                lambda rec: rec.has_friday == False)
            return [('id', 'in', res.ids)]

        res = self.env['sale.order'].search([])
        return [('id', 'in', res.ids)]

    def search_is_this_month_job(self, operator, value):
        """ Method to search current month jobs"""
        if operator == '=':
            agenda_ids = self.env['agenda.agenda'].search([])
            res = agenda_ids.filtered(
                lambda rec: rec.is_this_month_job)

            return [('id', 'in', res.ids)]
        if operator == '!=':
            agenda_ids = self.env['agenda.agenda'].search([])
            res = agenda_ids.filtered(
                lambda rec: rec.is_this_month_job == False)
            return [('id', 'in', res.ids)]

        res = self.env['agenda.agenda'].search([])
        return [('id', 'in', res.ids)]

    @api.depends('task_id.active')
    def compute_agenda_active(self):
        for rec in self:
            if rec.task_id:
                if rec.task_id.active:
                    rec.active = True
                else:
                    rec.active = False
            else:
                rec.active = True

    @api.depends('user_ids')
    def compute_user_names(self):
        """ Method to compute usernames """
        for rec in self:
            if rec.user_ids:
                rec.user_names = ','.join(rec.user_ids.mapped('name'))
            else:
                rec.user_names = ''

    @api.depends('vehicle_ids')
    def compute_vehicle_names(self):
        """ Method to compute vehicle names"""
        for rec in self:
            if rec.vehicle_ids:
                rec.vehicle_names = ','.join(rec.vehicle_ids.mapped('name'))
            else:
                rec.vehicle_names = ''

    @api.model
    @api.depends('user_ids')
    def _get_users(self):
        """ Fetch users set on the Many2many field Users to the field user_id_custom"""
        for rec in self:
            if rec.user_ids:
                user_custom = ','.join([p.name for p in rec.user_ids])
            else:
                user_custom = ''
            rec.user_id_custom = user_custom

    def find_field_services_within_time_range(self, date_start, date_end):
        """ Method to find field services within the given time range."""
        field_service_ids = self.env['project.task'].search(
            [('is_fsm', '=', True),
             '|',
             '|',
             '&',
             ('planned_date_begin', '>=', date_start),
             ('planned_date_begin', '<=', date_end),
             '&',
             ('date_deadline', '>=', date_start),
             ('date_deadline', '<=', date_end),
             '&',
             ('planned_date_begin', '<=', date_start),
             ('date_deadline', '>=', date_end)])
        return field_service_ids

    def find_helpdesk_tickets_within_time_range(self, date_start, date_end):
        """ Method to find helpdesk tickets within the given time range."""
        helpdesk_tickets = self.env['helpdesk.ticket'].search(
            [('stage_id.fold', '!=', True),
             '|',
             '|',
             '&',
             ('date_start', '>=', date_start),
             ('date_start', '<=', date_end),
             '&',
             ('date_end', '>=', date_start),
             ('date_end', '<=', date_end),
             '&',
             ('date_start', '<=', date_start),
             ('date_end', '>=', date_end)])
        return helpdesk_tickets

    def find_helpdesk_ticket_with_assigned_users(self, tickets):
        """ Search for the helpdesk tickets having assigned user is within the given users on agenda."""
        helpdesk_tickets = tickets.filtered(
            lambda l: l.user_id.id in [user for user in self.user_ids.ids])
        return helpdesk_tickets

    def find_helpdesk_ticket_with_assigned_resources(self, tickets):
        """ Search for the helpdesk tickets having assigned resource users on resource lines are
         within the given users on agenda."""
        helpdesk_tickets_with_resources = tickets.mapped(
            'resource_lines').filtered(
            lambda l: l.user_ids in [user_id for user_id in self.user_ids])
        return helpdesk_tickets_with_resources

    @api.depends('date_start', 'date_end')
    def compute_available_users(self):
        """ Compute all available users."""
        for rec in self:
            user_lines = []
            users = []
            field_service_ids = self.find_field_services_within_time_range(
                rec.date_start, rec.date_end)
            helpdesk_tickets = self.find_helpdesk_tickets_within_time_range(
                rec.date_start, rec.date_end)
            agenda_ids = self.env['agenda.agenda'].search(
                [('id', '!=', self._origin.id), ('date_start', '!=', False),
                 ('date_end', '!=', False)])
            if rec.date_start and rec.date_end:
                agenda_ids = agenda_ids.search(['|',
                                                '|',
                                                '&',
                                                ('date_start', '>=',
                                                 rec.date_start),
                                                ('date_start', '<=',
                                                 rec.date_end),
                                                '&',
                                                ('date_end', '>=',
                                                 rec.date_start),
                                                (
                                                    'date_end', '<=',
                                                    rec.date_end),
                                                '&',
                                                ('date_start', '<=',
                                                 rec.date_start),
                                                ('date_end', '>=',
                                                 rec.date_end)])
                if agenda_ids:
                    assigned_users = agenda_ids.mapped('user_ids')
                    for user in assigned_users:
                        users.append(user.id)
                if field_service_ids:
                    for ticket in field_service_ids:
                        users.extend(ticket.user_ids.ids)
                        for resource in ticket.co_user_ids:
                            users.append(resource.id)
                if helpdesk_tickets:
                    for ticket in helpdesk_tickets:
                        users.append(ticket.user_id.id)
                        for lines in ticket.resource_lines:
                            for user in lines.user_ids:
                                users.append(user.id)
                users = self.env['res.users'].search(
                    [('id', 'not in', users),
                     ('emp_id.new_divisions.name', '=ilike', 'Technical'),
                     ('emp_id.department_id', '!=', False),
                     ('emp_id.department_id.name', 'not ilike', 'Coordination')
                     ])
                for user in users:
                    line = (0, 0, {
                        "user_id": user.id,
                    })
                    user_lines.append(line)
                rec.available_user_ids = [(5, 0, 0)]
                rec.write({
                    'available_user_ids': user_lines
                })
            else:
                users = self.env['res.users'].search(
                    [('emp_id.new_divisions.name', '=ilike', 'Technical'),('emp_id.department_id', '!=', False),
                     ('emp_id.department_id.name', 'not ilike', 'Coordination')])
                for user in users:
                    line = (0, 0, {
                        "user_id": user.id,
                    })
                    user_lines.append(line)
                rec.available_user_ids = [(5, 0, 0)]
                rec.write({
                    'available_user_ids': user_lines
                })

    @api.constrains('user_ids')
    def onsave_users(self):
        """ Find the conflicted tasks for the users."""
        tickets = self.find_field_services_within_time_range(self.date_start,
                                                             self.date_end).filtered(
            lambda l: l.user_ids.ids in self.user_ids.ids)
        agendas = self.env['agenda.agenda'].search(
            [('date_start', '>=', self.date_start),
             ('date_end', '<=', self.date_end),
             ('id', '!=', self.id)]).filtered(
            lambda l: l.user_ids in [user_id for user_id in self.user_ids])
        helpdesk_tickets = self.find_helpdesk_tickets_within_time_range(
            self.date_start, self.date_end)
        helpdesk_tickets_with_assigned_users = self.find_helpdesk_ticket_with_assigned_users(
            helpdesk_tickets)
        helpdesk_tickets_with_assigned_resources = self.find_helpdesk_ticket_with_assigned_resources(
            helpdesk_tickets)
        if tickets or helpdesk_tickets_with_assigned_users or helpdesk_tickets_with_assigned_resources or agendas:
            self.is_conflicted = True
        else:
            self.is_conflicted = False

    def view_conflict_fs_tickets(self):
        """ Method to view conflicted field service tickets."""
        tickets = self.find_field_services_within_time_range(self.date_start,
                                                             self.date_end). \
            filtered(lambda
                         l: l.user_id.id in self.user_ids.ids and l.stage_id.state != 'done' and
                            l.stage_id.state != 'cancelled')
        if tickets:
            return {
                'type': 'ir.actions.act_window',
                'view_id': self.env.ref(
                    'industry_fsm.project_task_view_kanban_fsm').id,
                'name': 'FS Tickets',
                'view_type': 'kanban',
                'view_mode': 'kanban',
                'res_model': 'project.task',
                'views': [(self.env.ref(
                    'industry_fsm.project_task_view_kanban_fsm').id, 'kanban'),
                          (self.env.ref(
                              'industry_fsm.project_task_view_list_fsm').id,
                           'list'),
                          (self.env.ref(
                              'industry_fsm.project_task_view_form').id,
                           'form')],
                'domain': [('id', 'in', tickets.ids),
                           ('id', '!=', self.task_id.id),
                           ('stage_id.state', '!=', 'done'),
                           ('stage_id.state', '!=', 'cancelled')],
                'target': 'current'
            }

    def view_conflict_helpdesk_tickets(self):
        """ Method to view conflicted helpdesk tickets."""

        helpdesk_tickets = self.find_helpdesk_tickets_within_time_range(
            self.date_start, self.date_end)
        helpdesk_tickets_with_assigned_users = self.find_helpdesk_ticket_with_assigned_users(
            helpdesk_tickets)

        helpdesk_tickets_with_assigned_resources = self.find_helpdesk_ticket_with_assigned_resources(
            helpdesk_tickets).mapped('helpdesk_ticket_id')
        if helpdesk_tickets_with_assigned_resources or helpdesk_tickets_with_assigned_users:
            return {
                'type': 'ir.actions.act_window',
                'view_id': self.env.ref(
                    'helpdesk.helpdesk_ticket_view_kanban').id,
                'name': 'Helpdesk Tickets',
                'view_type': 'kanban',
                'view_mode': 'kanban',
                'res_model': 'helpdesk.ticket',
                'views': [(self.env.ref(
                    'helpdesk.helpdesk_ticket_view_kanban').id, 'kanban'),
                          (self.env.ref(
                              'helpdesk.helpdesk_tickets_view_tree').id,
                           'list'),
                          (
                              self.env.ref(
                                  'helpdesk.helpdesk_ticket_view_form').id,
                              'form')],
                'domain': ['|', (
                    'id', 'in', helpdesk_tickets_with_assigned_resources.ids),
                           (
                               'id', 'in',
                               helpdesk_tickets_with_assigned_users.ids)
                           ],
                'target': 'current'
            }

    def view_conflict_agendas(self):
        """ Method to view conflicted agendas."""
        agendas = self.env['agenda.agenda'].search(
            [('date_start', '>=', self.date_start),
             ('date_end', '<=', self.date_end), ('id', '!=', self.id)])
        agenda_ids = []
        for user in self.user_ids:
            conflicted_agendas = agendas.filtered(lambda l: user in l.user_ids)
            for agnda in conflicted_agendas:
                agenda_ids.append(agnda.id)

        if agenda_ids:
            action = {
                'type': 'ir.actions.act_window',
                'name': 'Agendas',
                'view_type': 'kanban',
                'view_mode': 'kanban,form',
                'res_model': 'agenda.agenda',
                'domain': [('id', 'in', agenda_ids)],
                'target': 'current'
            }
            return action

    @api.depends('task_id')
    def compute_task_range(self):
        """ Method to compute task ranges."""
        for rec in self:
            rec.date_start = rec.task_id.planned_date_begin
            rec.date_end = rec.task_id.date_deadline


class AvailableResources(models.Model):
    """ Available resources"""
    _name = 'available.resource'

    user_id = fields.Many2one('res.users', string="Resources Available")
    agenda_id = fields.Many2one('agenda.agenda')
