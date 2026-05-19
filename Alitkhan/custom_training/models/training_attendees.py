from odoo import fields, models

class TrainingAttendees(models.Model):
    _name = "attendees.attendees"
    _description =  "Attendees"

    name = fields.Char(string="Name")
    job_position_id = fields.Many2one("attendees.position", string="Job Position")
    work_location_id = fields.Many2one('work.location', string="Work Location")
    phone = fields.Char(string="Phone")

    def merge_attendees(self):
        tarining_attendees_ids = self.env['training.attendees'].search(
            [('attendee_id', 'in', self.ids)])
        i = 0
        for attendee in self:
            if i == 0:
                pass
            else:
                if attendee.job_position_id:
                    if self[0].job_position_id:
                        pass
                    else:
                        self[0].job_position_id = attendee.job_position_id.id
                if attendee.work_location_id:
                    if self[0].work_location_id:
                        pass
                    else:
                        self[0].work_location_id = attendee.work_location_id
                if attendee.phone:
                    if self[0].phone:
                        pass
                    else:
                        self[0].phone = attendee.phone
                for training_attendee in tarining_attendees_ids:
                    training_attendee.attendee_id = self[0].id
                attendee.unlink()
            i = i + 1