# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError
import datetime
import dateutil #user to create time delta


class HelpdeskTicket(models.Model):
    _inherit = "helpdesk.ticket"

    pm_id = fields.Many2one('preventive.maintainence', readonly=True, copy=False)

class ContractProduct(models.Model):
    _inherit = "contract.product"
    pm_id = fields.Many2one('preventive.maintainence', readonly=True, copy=False)

class ContractContract(models.Model):
    _inherit = "contract.contract"

    pm_created = fields.Boolean(string="PM Tickets Created" ,readonly=True, copy=False)
    interval = fields.Selection([("3","Three"), ("6","Six"), ("9","Nine"), ("12","Twelve")], string="PM Interval")

    def generated_pm_records(self):
        contracts = self.env['contract.contract'].search([('pm_created', '=', False), ('interval', '!=', False)])
        for contract_id in contracts:
            pm_created = False

            for contract_line_id in contract_id.product_lines.filtered(lambda x: not x.pm_id and x.eoc_date > x.starting_date):

                new_values = {
                    'sn': contract_line_id.sn,
                    'ref': 'eoc',
                    'interval': contract_id.interval
                }

                pm_id = self.env['preventive.maintainence'].create(new_values)

                pm_id.search_sn()
                pm_id.generate_dates_table()
                pm_id.set_active()
                contract_line_id.pm_id = pm_id.id
                pm_created = True

            contract_id.pm_created = pm_created

class PreventiveMaintainence(models.Model):
    _name = 'preventive.maintainence'
    _inherit='mail.thread'
    _rec_name = "name"

    name = fields.Char(string="Name",compute="compute_name") 
    sn = fields.Char(string="Serial Number",required=True) 
    iq = fields.Char(string="IQ Number") 
    interval_days = fields.Integer(string="Interval Days", help="The number to create tickets in advance", default=5)
    starting_date = fields.Date(string="Starting Date",readonly=True)
    eoc_date = fields.Date(string="EOC Date",readonly=True)

    """ ref : it has two conditions 
    eoc : means that the eoc date will be the end of service date
    manual : means that theuser will manuallt enter service years """
    ref = fields.Selection([("eoc","Use EOC") ,("manual","Insert Service Years manually")], default="eoc", string="Usage")

    """ if ref is 'eoc' """
    service_years = fields.Integer(string="Service Year")

    """ service inteval, example : every 3 months,6 or year """
    interval = fields.Selection([("3","Three"), ("6","Six"), ("9","Nine"), ("12","Twelve")], string="Interval", default="3",required=True)

    """ service schedule, will be used by the cron job """
    pm_date_lines = fields.One2many("preventive.maintainence.dates","pm_id", string="Preventive Maintainence Schedule")

    """ only active tickets will be considered by the cron job """
    status = fields.Selection([("draft","Draft"),("active","Active"), ("archvied","Archived")], default="draft")

    """ Searches for all Preventive maintainence line items for date that are passed and creates a helpdesk ticket, 
    then sets it to done so that it doesnt appear in future searches """
    def _pm_watch(self):
        preventive_maintainence_dates_ids = self.env["preventive.maintainence.dates"].search([("pm_id.status","=","active"),("is_done","=",False)])
        if preventive_maintainence_dates_ids:
            for item in preventive_maintainence_dates_ids:
                creation_date = item.date - datetime.timedelta(days=item.pm_id.interval_days)
                if creation_date == datetime.date.today():
                    helpdesk_ticket_id = self.env["helpdesk.ticket"].create({"sn_search":item.pm_id.sn,"pm_id":item.pm_id.id})
                    helpdesk_ticket_id.search_by_sn()
                    item.is_done = True
                    item.pm_id.message_post(body=f"A new helpdesk ticket was created at {datetime.datetime.today()}, Ticket id : {helpdesk_ticket_id.id}, Line Id : {item.id}")
                else:
                    pass
        else:
            pass


    def set_active(self):
        for line in self.pm_date_lines:
            line.is_done = False
        self.status = "active"

    def reset_draft(self):
        self.status = "draft"

    def set_archive(self):
        self.status="archived"


    def compute_name(self):
        for rcd in self:
            rcd.name = "PM - " + str(rcd.id)

    
    """ Prevents user from deleting active and archived records """
    
    def unlink(self):
        for rcd in self:
            if rcd.status == 'active' or rcd.status == 'archived':
                raise UserError(_("You cannot delete and active or archived ticket")) 
            else:
                res = super(PreventiveMaintainence,self).unlink()
                return res


    def generate_dates_table(self):
        list_of_dates = []
        increment = dateutil.relativedelta.relativedelta(months=int(self.interval))
        final_date = self.eoc_date if self.ref == "eoc" else (self.starting_date + dateutil.relativedelta.relativedelta(years=self.service_years))
        loop = (self.eoc_date - self.starting_date).days / 30 if self.ref == "manual" else (final_date - self.starting_date ).days / 30   #Number of increments
        """ if eoc date is before PAC date """
        if loop < 0:
            raise UserError(_("EOC date can`t be before PAC Date"))

        """ first index of loop, list_of_dates is empty, this only happens one time, 
        then It will take the last element in list and increment it """
        while loop > 0:
            if not list_of_dates:
                new_date = self.starting_date + increment

                if new_date < final_date:
                    list_of_dates.append(new_date)

                    loop-=1
            else:
                new_date = list_of_dates[-1] + increment

                if new_date < final_date:
                    list_of_dates.append(new_date)

                    loop-=1
                else:
                    loop-=1
                    pass

        self.write( {"pm_date_lines":[ (5, 0) ] } )
        for item in list_of_dates:

            self.write({"pm_date_lines":[(0,0,{"date":item,"is_done":False})]})

    """ populates dates fields """

    def search_sn(self):
        if not self.sn:
            raise UserError (_("Please fill in Serial Number before clicking Search"))


        product_ids = self.env['contract.product'].search([('sn', 'like', self.sn )], order="starting_date")

        if len(product_ids) == 0:
            raise UserError(_(f"No Conrtact was found with for serial number {self.sn}"))
        if len(product_ids) == 1:

            self.starting_date = product_ids.starting_date
            self.eoc_date = product_ids.eoc_date
            self.iq  = product_ids.contract_id.iq

        if len(product_ids) > 1:
            self.starting_date = product_ids[-1].starting_date
            self.eoc_date = product_ids[-1].eoc_date
            self.iq  = product_ids[-1].contract_id.iq


class PreventiveMaintainenceDates(models.Model):
    _name = 'preventive.maintainence.dates'

    pm_id = fields.Many2one("preventive.maintainence")
    date = fields.Date(string="Date")
    is_done = fields.Boolean(string="Done")
