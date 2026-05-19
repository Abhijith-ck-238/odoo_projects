from odoo import api,fields, models


class FleetVehicle(models.Model):
    _inherit = 'fleet.vehicle'

    STATUS = [("1", "Available"), ("2", "On Trip"), ("3", "In Maintainence"),
              ("4", "Reserved")]

    odometer = fields.Float(compute="_get_odometer", inverse='_set_odometer',
                            string='Odometer Value',
                            help='Odometer measure of the vehicle at the moment of this log', tracking=True)
    car_status = fields.Selection(STATUS, string="Current Status", tracking=True)
    current_users = fields.Many2many('res.users', compute="compute_current_users_and_province")
    province_ids = fields.Many2one('contract.province', compute="compute_current_users_and_province")
    province_id = fields.Integer()
    site_id = fields.Many2one('contract.site', compute="compute_current_users_and_province")
    job_count = fields.Integer("Jobs", compute="compute_current_users_and_province")


    def compute_current_users_and_province(self):
        for rec in self:
            tickets = self.env['project.task'].search([('vehicle_ids', '=', rec.id),('planned_date_begin', '<=', fields.Date.today()), ('planned_date_end', '>=', fields.Date.today())],limit=1, order='id asc')
            ticket_count = self.env['project.task'].search_count(
                [('vehicle_ids', '=', rec.id),
                 ('planned_date_begin', '<=', fields.Date.today()),
                 ('planned_date_end', '>=', fields.Date.today())])
            users = []
            users.append(tickets.user_id.id)
            users += tickets.co_user_ids.ids
            if tickets:
                rec.current_users = users
                rec.province_ids = tickets.province.id
                rec.site_id = tickets.site_id.id
                rec.job_count = ticket_count
            else:
                rec.province_ids = False
                rec.current_users = False
                rec.site_id = False
                rec.job_count = 0


    def send_message(self, rec_id="", lp="", car_model="", service_type="",
                     car_tag=""):  # takes in record_id and record_name
        channel_id = self.env['discuss.channel'].search(
            [('name', '=', 'Vehicles Service notifications')])
        if not channel_id:
            channel_id = self.env['discuss.channel'].create(
                {"name": "Vehicles Service notifications"})

        notification = (
                           '<div class="fleet.vehicle"><a href="#" class="o_redirect" data-oe-model = "fleet.vehicle" data-oe-id="%s">#Number : %s- Model : %s - Car Tag : %s</a></div>') % (
                       rec_id, lp, car_model, car_tag)
        for rec in channel_id:
            rec.message_post(
                body='Automated Message : The Following Vehicle Requires %s :' % service_type + notification,
                subtype_xmlid='mail.mt_comment')

