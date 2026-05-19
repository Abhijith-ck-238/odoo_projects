from odoo import models, fields, _
import pytz
from odoo.exceptions import UserError


class ReservationWizard(models.TransientModel):
    _name = "reservation.wizard"
    _description = "Reservation Wizard"

    employee_id = fields.Many2one('hr.employee', 'Employee', default=lambda
        self: self.env.user.employee_id)
    start_date = fields.Datetime("Start Date")
    end_date = fields.Datetime("End Date")

    def action_reserve(self):
        bed = self.env['guest.house.bed'].browse(
            self.env.context.get('active_id'))

        # Get the current datetime but set hours, minutes, seconds to 0
        today_start = fields.Datetime.now().replace(hour=0, minute=0, second=0,
                                                    microsecond=0)

        # Add validation to prevent reservations in the past
        if self.start_date and self.start_date < today_start:
            raise UserError(_('You cannot select a past date for reservation.'))

        reservations = self.env['bed.reservation'].search([
            ('bed_id', '=', self.env.context.get('active_id')),
            ('date_to', '>=', today_start),
            # Changed to today's start instead of current time
            ('date_from', '<', self.end_date),
            ('date_to', '>', self.start_date),
            ('state', '!=', 'cancelled')
        ], order='date_from asc')
        if reservations:
            string = ''
            for rec in reservations:
                if string != "":
                    string += ', '
                tz = self.env.user.tz or 'UTC'
                att_tz = pytz.timezone(tz)
                date_from = fields.Datetime.from_string(rec.date_from).replace(
                    tzinfo=pytz.utc).astimezone(att_tz)
                date_to = fields.Datetime.from_string(rec.date_to).replace(
                    tzinfo=pytz.utc).astimezone(att_tz)
                from_date_formatted = date_from.strftime('%Y-%m-%d %I:%M:%S %p')
                to_date_formatted = date_to.strftime('%Y-%m-%d %I:%M:%S %p')
                string += from_date_formatted + ' to ' + to_date_formatted
            raise UserError(
                _('The bed is already reserved for ' + string + '.'))
        else:
            # Additional validation - ensure end date is after start date
            if self.end_date <= self.start_date:
                raise UserError(_('End date must be after start date.'))
            self.env['bed.reservation'].sudo().create({
                'employee_id': self.employee_id.id,
                'bed_id': self.env.context.get('active_id'),
                'guest_house_id': bed.guest_house_id.id,
                'date_from': self.start_date,
                'date_to': self.end_date
            })
