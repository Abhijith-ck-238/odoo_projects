from odoo import models, fields, api
from odoo.exceptions import UserError

class CalendarEvent(models.Model):
    _inherit = "calendar.event"

    send_email_to_attendees = fields.Boolean(string="Send Email")


class Attendee(models.Model):
    _inherit = "calendar.attendee"

    def _send_mail_to_attendees(self, mail_template, force_send=False):
        for rec in self:
            if not rec.event_id.send_email_to_attendees:
                pass
            else:
                res = super(Attendee, self)._send_mail_to_attendees(mail_template=mail_template, force_send=force_send)
                return res
