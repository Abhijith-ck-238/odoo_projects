from odoo import fields, models
import json
from odoo.tools import json_default
from datetime import timedelta, datetime
import calendar
import io

try:
    from odoo.tools.misc import xlsxwriter
except ImportError:
    import xlsxwriter


class FieldServiceTaskXlsReport(models.TransientModel):
    _name = "field.service.task.xlsx.report"
    start_date = fields.Date(string="Start Date")
    end_date = fields.Date(string="End Date")
    user_id = fields.Many2one('res.users', string="User")
    old_version_report = fields.Boolean(string="Ver 1")

    def print_xlsx(self):
        data = {
            'form_data': self.read()[0],
            'month': self.start_date.month,
            'year': self.start_date.year,
        }
        return {
            'type': 'ir.actions.report',
            'data': {'model': 'field.service.task.xlsx.report', 'options': json.dumps(data, default=json_default),
                     'output_format': 'custom_helpdesk_xlsx', 'report_name': 'Export Template'},
            'report_type': 'custom_helpdesk_xlsx'}
        # return self.env.ref('custom_helpdesk.action_field_service_task_report_xlsx').report_action(self, data=data)

    def generate_xlsx_report(self, data, response):
        """ Method to generate an xlsx report of agendas for each individual users"""
        record_id = data.get('record_id')
        record = self.browse(record_id)

        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})

        version = data['form_data']["old_version_report"]
        start_date = data['form_data']["start_date"]
        end_date = data['form_data']["end_date"]
        total_days_in_month = calendar.monthrange(data['year'], data['month'])[1]

        total_fridays_in_month = len([1 for i in calendar.monthcalendar(data['year'],
                                                                        data['month']) if i[4] != 0])
        total_days_in_month = total_days_in_month - total_fridays_in_month
        agenda_ids = self.env['agenda.agenda'].search(
            [('task_id', '!=', False)])
        sheet = workbook.add_worksheet('Task Analysis')
        bold = workbook.add_format({'bold': True})
        sheet.write(1, 2, 'Start Date', bold)
        sheet.write(1, 3, start_date, bold)
        sheet.write(1, 4, 'End Date', bold)
        sheet.write(1, 5, end_date, bold)
        row = 3
        col = 1
        sheet.write(row, col, 'User', bold)
        sheet.write(row, col + 1, 'Total Working Days', bold)
        sheet.write(row, col + 2, 'Total Working Fridays', bold)
        sheet.write(row, col + 3, 'Stand By Days', bold)
        sheet.write(row, col + 4, 'Total Off Days', bold)
        sheet.write(row, col + 5, 'Total Tickets', bold)
        sheet.write(row, col + 6, 'Total Done Tickets', bold)

        if data['form_data']['user_id']:
            user_id = self.env['res.users'].browse(
                data['form_data']['user_id'][0])
            user_details = self.get_fs_details_user(agenda_ids,
                                                    user_id.id, start_date,
                                                    end_date,
                                                    total_days_in_month,
                                                    version)
            row = row + 1
            sheet.write(row, col, user_id.name)
            sheet.write(row, col + 1, user_details["total_working_days"])
            sheet.write(row, col + 2, user_details["friday_count"])
            sheet.write(row, col + 3, user_details["stand_by_days"])
            sheet.write(row, col + 4, user_details["total_time_off"])
            sheet.write(row, col + 5, user_details["total_ticket_count"])
            sheet.write(row, col + 6, user_details["total_done_ticket_count"])
        else:
            users = agenda_ids.mapped('user_ids')
            for user in users:
                if user:
                    user_details = self.get_fs_details_user(agenda_ids,
                                                            user.id,
                                                            start_date,
                                                            end_date,
                                                            total_days_in_month,
                                                            version)

                    user_id = self.env['res.users'].browse(user.id)
                    row = row + 1
                    sheet.write(row, col, user_id.name)
                    sheet.write(row, col + 1,
                                user_details["total_working_days"])
                    sheet.write(row, col + 2, user_details["friday_count"])
                    sheet.write(row, col + 3, user_details["stand_by_days"])
                    sheet.write(row, col + 4, user_details["total_time_off"])
                    sheet.write(row, col + 5, user_details["total_ticket_count"])
                    sheet.write(row, col + 6, user_details["total_done_ticket_count"])
        workbook.close()
        output.seek(0)
        response.stream.write(output.read())
        output.close()

    def get_fs_details_user(self, tasks, user, start_date, end_date,
                            total_days_in_month, version):
        """Method to get the xlsx report details for individual users."""
        month_allocations = {}
        friday_allocations = {}
        friday_off = {}
        for i in range(1, total_days_in_month + 1):
            if i < 10:
                formatted_number = '{:02d}'.format(i)
                month_allocations[formatted_number] = False
                friday_allocations[formatted_number] = False
                friday_off[formatted_number] = False
            else:
                month_allocations[i] = False
                friday_allocations[i] = False
                friday_off[i] = False
        agendas = tasks.search(
            [('user_ids', 'in', user),
             ('task_id', '!=', False),
             '|',
             '|',
             '&',
             ('date_start', '>=', start_date),
             ('date_start', '<=', end_date),
             '&',
             ('date_end', '>=', start_date),
             ('date_end', '<=', end_date),
             '&',
             ('date_start', '>=', start_date),
             ('date_end', '<=', end_date)])
        agendas_done = tasks.search(
            ['|', ('x_studio_stage', '=', 18), ('x_studio_stage', '=', 22),
             ('user_ids', 'in', user),
             ('task_id', '!=', False),
             '|',
             '|',
             '&',
             ('date_start', '>=', start_date),
             ('date_start', '<=', end_date),
             '&',
             ('date_end', '>=', start_date),
             ('date_end', '<=', end_date),
             '&',
             ('date_start', '>=', start_date),
             ('date_end', '<=', end_date)])
        total_ticket_count = len(agendas.ids)
        total_done_ticket_count = len(agendas_done.ids)
        for tas in agendas:
            date_endd = datetime.strptime(end_date, '%Y-%m-%d').date()
            date_startt = datetime.strptime(start_date, '%Y-%m-%d').date()
            if tas.date_end.date() > date_endd and tas.date_start.date() < date_startt:
                self.allocate_days_on_months(date_startt, date_endd, friday_allocations, month_allocations)
            elif tas.date_end.date() > date_endd:
                self.allocate_days_on_months(tas.date_start.date(), date_endd, friday_allocations, month_allocations)
            elif tas.date_start.date() < date_startt:
                self.allocate_days_on_months(date_startt, tas.date_end.date(), friday_allocations, month_allocations)
            else:
                self.allocate_days_on_months(tas.date_start.date(), tas.date_end.date(), friday_allocations,
                                             month_allocations)
        duplicates = {key: value for key, value in
                      month_allocations.items() if
                      value}
        count = len(duplicates)
        fridays = {key: value for key, value in
                   friday_allocations.items() if
                   value}
        friday_count = len(fridays)
        total_working_days = count
        agenda_ids = tasks.search(
            [('user_ids', 'in', user),
             ('task_id', '=', False),
             '|',
             '|',
             '&',
             ('date_start', '>=', start_date),
             ('date_start', '<=', end_date),
             '&',
             ('date_end', '>=', start_date),
             ('date_end', '<=', end_date),
             '&',
             ('date_start', '>=', start_date),
             ('date_end', '<=', end_date)])
        total_time_off_count = 0.0
        for task in agenda_ids:
            hr_leave_id = self.env['hr.leave'].search([('agenda_id', '=', task.id)])
            date_endd = datetime.strptime(end_date, '%Y-%m-%d').date()
            date_startt = datetime.strptime(start_date, '%Y-%m-%d').date()
            if hr_leave_id.request_date_to > date_endd and hr_leave_id.request_date_from < date_startt:
                self.allocate_off_on_months(date_startt, date_endd, friday_off)
                friday = {key: value for key, value in
                          friday_off.items() if
                          value}
                friday_off_count = len(friday)
                duration = (date_endd - date_startt).days + 1 - friday_off_count
            elif hr_leave_id.request_date_to > date_endd:
                self.allocate_off_on_months(hr_leave_id.request_date_from, date_endd, friday_off)
                friday = {key: value for key, value in
                          friday_off.items() if
                          value}
                friday_off_count = len(friday)
                duration = (date_endd - hr_leave_id.request_date_from).days + 1 - friday_off_count
            elif hr_leave_id.request_date_from < date_startt:
                self.allocate_off_on_months(date_startt,
                                            hr_leave_id.request_date_to, friday_off)
                friday = {key: value for key, value in
                          friday_off.items() if
                          value}
                friday_off_count = len(friday)
                duration = (hr_leave_id.request_date_to - date_startt).days + 1 - friday_off_count
            else:
                duration = hr_leave_id.number_of_days
            total_time_off_count = total_time_off_count + duration
        stand_by_days = total_days_in_month - total_working_days - total_time_off_count
        if not version:
            if stand_by_days < 0:
                total_working_days -= abs(stand_by_days)
                stand_by_days = 0
        return {"total_working_days": total_working_days,
                "friday_count": friday_count,
                "stand_by_days": stand_by_days,
                "total_time_off": total_time_off_count,
                "total_ticket_count": total_ticket_count,
                "total_done_ticket_count": total_done_ticket_count,
                }

    def allocate_days_on_months(self, date_start, date_end, friday_allocations, month_allocations):
        """Method to allocate days on month"""
        diff = date_end - date_start
        if diff.days == 0:
            dayy = str(date_start.strftime('%d'))
            if date_start.weekday() == 4:
                friday_allocations[str(dayy)] = True
            month_allocations[str(dayy)] = True
        else:
            for i in range(diff.days + 1):
                day = date_start + timedelta(days=i)
                dayy = str(day.strftime('%d'))
                if day.weekday() == 4:
                    friday_allocations[str(dayy)] = True
                month_allocations[str(dayy)] = True

    def allocate_off_on_months(self, date_start, date_end, friday_off):
        """Method to allocate days on month"""
        diff = date_end - date_start
        if diff.days == 0:
            dayy = str(date_start.strftime('%d'))
            if date_start.weekday() == 4:
                friday_off[str(dayy)] = True
        else:
            for i in range(diff.days + 1):
                day = date_start + timedelta(days=i)
                dayy = str(day.strftime('%d'))
                if day.weekday() == 4:
                    friday_off[str(dayy)] = True
