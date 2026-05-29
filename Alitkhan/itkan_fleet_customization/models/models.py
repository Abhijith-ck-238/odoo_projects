# -*- coding: utf-8 -*-
from markupsafe import Markup

from odoo import models, fields, api, _
from odoo.exceptions import UserError
import datetime

class FleetVehicleExt(models.Model):
    _inherit = "fleet.vehicle"

    STATUS=[("1","Available"),("2","On Trip"),("3","In Maintainence"),("4","Reserved")]
    
    display_name = fields.Char(compute="_gen_name")

    car_registration = fields.Many2many(comodel_name="ir.attachment",
                                relation="car_attachement_rel", 
                                column1="car_id",
                                column2="attachment_id",
                                string="Car Registration")
    trips_count = fields.Integer(compute="_compute_trips_count")

    car_status = fields.Selection(STATUS,string="Current Status")
    car_tag = fields.Char()
    vehicle_category_id = fields.Many2one("vehicle.category",string="Category")
    category_image = fields.Binary(related="category_id.icon")
    sequence = fields.Integer(string="Kanban View Sequence")
    service_lines = fields.One2many("service.intervals","vehicle_id",string="Service Lines")

    current_user_is_admin = fields.Boolean(default=True)
    has_access_service = fields.Boolean(compute="compute_has_access_service")

    @api.model
    def create(self, vals):
        res = super(FleetVehicleExt, self).create(vals)
        car_registration = res.mapped('car_registration')
        car_registration.write({
            'res_id': res.id,
        })
        return res


    def compute_has_access_service(self):
        for rcd in self:
            if rcd.env.user.has_group('itkan_fleet_customization.fleet_technician') :
                rcd.has_access_service = True
            else:
                rcd.has_access_service = False

    # def compute_current_user_is_admin(self):
    #     for rcd in self:
    #         if rcd.env.user.has_group('fleet.fleet_group_manager') :
    #             rcd.current_user_is_admin = True
    #         else:
    #             rcd.current_user_is_admin = False

    @api.depends("model_id", "car_tag", "license_plate")
    def _gen_name(self):
        for vehicle in self:
            name = ""
            if vehicle.car_tag:
                name += vehicle.car_tag + ' - '
            if vehicle.model_id:
                name +=  vehicle.model_id.name
            if vehicle.license_plate:
                name += '/' + vehicle.license_plate

            vehicle.display_name = name


    def name_get(self):
        result = []
        for record in self:
            result.append((record.id, record.display_name))
        return result

    @api.onchange("odometer")
    def check_odometer_readings(self):
        for rcd in self:
            for line in rcd.service_lines:
                if line:
                    if line.next_service < rcd.odometer:
                        self.send_message(rec_id = rcd._origin.id,service_type=line.service_type.name,lp=rcd.license_plate,car_model=rcd.model_id.name,car_tag=rcd.car_tag)
                else:
                    pass
            
    def send_message(self,rec_id="",lp="",car_model="",service_type="",car_tag=""): #takes in record_id and record_name
       
        channel_id = self.env['discuss.channel'].search([('name', '=', 'Vehicles Service notifications')])
        if not channel_id:
            channel_id = self.env['discuss.channel'].create({"name":"Vehicles Service notifications"})
        notification = Markup((
                           '<div class="fleet_vehicle">'
                           '<a href="#" class="o_redirect" data-oe-model="fleet.vehicle" data-oe-id="%s">'
                           '#Number: %s - Model: %s - Car Tag: %s'
                           '</a></div>'
                       )
                        % (rec_id, lp, car_model, car_tag))

        channel_id.message_post(
                    body='Automated Message: The Following Vehicle Requires %s :' % service_type + notification,
                    subtype_xmlid='mail.mt_comment')
        

# This is not needed as vehicle_id in service_report is not used

    def _compute_trips_count(self):
        for rcd in self:
            rcd.trips_count = len(self.env["service.report"].search([("vehicle_id","=",rcd.id)]))



    def redirect_to_service(self,context={}):
        form_view_id = self.env.ref("service_reports.service_report_form").id
        tree_view_id = self.env.ref("service_reports.service_report_tree").id
        context.update({"vehicle_id":self.id})
        return {
            'type': 'ir.actions.act_window',
            'name': 'Service Reports',
            'view_type': 'form',
            'view_mode': 'list',
            'res_model': 'service.report',
            'views': [(tree_view_id,'list'),(form_view_id, 'form')],
            'domain': [('vehicle_id', '=', self.id)],
            'target': 'current',
            'context':context,            
        }



class ServiceIntervals(models.Model):
    _name="service.intervals"

    vehicle_id = fields.Many2one("fleet.vehicle")
    service_type = fields.Many2one("fleet.service.type",string="Service Type")
    service_interval = fields.Integer(string="Service Interval")
    next_service = fields.Integer(string="Next Service",readonly=True)
    km_left = fields.Integer(string="Left to next service",readonly=True,compute="compute_km_left")
    display_kanban = fields.Boolean()

    def compute_km_left(self):
        for rcd in self:
            if rcd.next_service:
                rcd.km_left =  rcd.next_service - rcd.vehicle_id.odometer 
            else:
                rcd.km_left = 0

    def reset_next_service(self):
        self.next_service = self.vehicle_id.odometer + self.service_interval  
        self.vehicle_id.message_post(body="The service interval has been reset by %s in %s" %(self.env.user.name, datetime.datetime.now().strftime("%m/%d/%Y, %H:%M:%S")))  
    
    @api.model
    def create(self,vals):
        res= super(ServiceIntervals,self).create(vals)
        res.next_service = res.service_interval + res.vehicle_id.odometer
        return res



#Deprecated, now service type is linked to odoo default service type
# class ServiceType(models.Model):
#     _name="service.type"
#     _rec_name = "name"

#     name=fields.Char(string="Service type")


class FleetVehicleLogServicesExt(models.Model):
    _inherit="fleet.vehicle.log.services"

    irregular_service = fields.Boolean(string="Irregular Service")


class FleetVehicleModelCategory(models.Model):
    _inherit = "fleet.vehicle.model.category"

    icon =fields.Binary(string="Icon")
