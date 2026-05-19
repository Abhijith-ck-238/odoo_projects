from odoo import fields, models


class TrainingAttendees(models.Model):
    _name = "training.attendees"
    _description = "Training Attendees"

    attendee_id = fields.Many2one('attendees.attendees', string='Attendee')
    position = fields.Many2one('attendees.position',string="Position", related="attendee_id.job_position_id")
    document = fields.Many2many('ir.attachment',string="Document")
    training_id = fields.Many2one('training.ticket')
    work_location_id = fields.Many2one('work.location', string="Work Location", related="attendee_id.work_location_id")
    phone = fields.Char(string="Phone", related="attendee_id.phone")

    @api.model
    def create(self, vals):
        res = super(TrainingAttendees, self).create(vals)
        document = res.mapped('document')
        document.write({
            'res_id': res.id,
        })
        return res

