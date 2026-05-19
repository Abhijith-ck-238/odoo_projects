from odoo import api, fields, models

class ServiceIntervals(models.Model):
    _inherit = "service.intervals"

    odometer_value = fields.Float('Odometer', compute="compute_odometer")
    is_activity_scheduled = fields.Boolean()
    state_id = fields.Char()

    @api.depends('vehicle_id')
    def compute_odometer(self):
        for rec in self:
            rec.odometer_value = rec.vehicle_id.odometer
            if rec.service_type != False and rec.service_type.notify_before_km > 0:
                if not rec.is_activity_scheduled:
                    if rec.odometer_value >= rec.next_service - rec.service_type.notify_before_km:
                        users = self.env.ref("fleet.fleet_group_manager").users
                        for user in users:
                            self.env['mail.activity'].create({
                                'display_name': 'Fleet Reminder',
                                'summary': 'Fleet Reminder',
                                'note': 'The ' + str(rec.service_type.name) + ' for ' +
                                        str(rec.vehicle_id.model_id.name) + ' require attention upon reaching '+
                                        str(rec.odometer_value)+ '-' + str(rec.service_type.notify_before_km),
                                'date_deadline': fields.datetime.now(),
                                'user_id': user.id,
                                'res_id': rec.vehicle_id.id,
                                'res_model_id': self.env['ir.model'].sudo().search([('model', '=', 'fleet.vehicle')], limit=1).id,
                                'activity_type_id': self.env.ref("mail.mail_activity_data_todo").id
                            })
                        rec.is_activity_scheduled = True

    def reset_next_service(self):
        res = super(ServiceIntervals,self).reset_next_service()
        self.is_activity_scheduled = False
        return res
