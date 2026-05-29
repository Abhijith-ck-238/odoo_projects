from dateutil.relativedelta import relativedelta
from odoo import models, fields, _, api
import datetime
from num2words import num2words
from odoo.exceptions import UserError
import dateutil


class CustomPreventiveMaintainence(models.Model):
    """ Class inherits Preventive Maintenance"""
    _inherit = 'preventive.maintainence'
    def _ondelete_interval(self,records):
        records.write({
            'interval': '1'
        })
    active = fields.Boolean(string="Active", default=True)
    interval = fields.Selection(
        selection_add=[("1", "One Month"), ("2", "Two Month"),
                       ("3", "Three Month"), ("4", "Four Month"),
                       ("5", "Five Month"),
                       ("6", "Six Month"), ("7", "Seven Month"),
                       ("8", "Eight Month"), ("9", "Nine Month"),
                       ("10", "Ten Month"), ("11", "Eleven Month"),
                       ("12", "Twelve Month")], default="1", string="Frequency",
        required=True, ondelete={'1': 'set default', '2': 'set default', '3': 'set default','4': 'set default',
                                 '5': 'set default', '6': 'set default','7': 'set default', '8': 'set default',
                                 '9': 'set default','10': 'set default', '11': 'set default', '12': 'set default'} )
    modality = fields.Many2one('contract.modality', string="Modality",
                               compute='compute_modality',
                               store=True)
    this_month = fields.Boolean(string="This Month")
    next_month = fields.Boolean(string="Next Month")
    interval_days = fields.Integer(string="Interval Days",
                                   help="The number to create tickets in advance",
                                   default=0)
    total_no_of_years = fields.Integer(string="Total Number of years")
    contract_id = fields.Many2one('contract.contract', string="Contract")
    contract_product_id = fields.Many2one('contract.product',
                                          string="Contract Product")
    product_char = fields.Char(string="Product",
                               related='contract_product_id.product_char')
    # province = fields.Many2one('contract.province', string="Province",
    #                            related='contract_product_id.province')
    site = fields.Many2one('contract.site', string="Site",
                           related='contract_product_id.site')

    def get_filter_records(self, start_date, end_date):
        pm_line_record = self.env['preventive.maintainence.dates'].search([('pm_rounded_date', '>=', start_date), ('pm_rounded_date', '<=', end_date)]).mapped('pm_id.id')
        return list(set(pm_line_record))

    def assign_contract_on_pm(self):
        """ Scheduled action to assign contract on old preventive maintenance which doesn't have contract id in it."""
        pm_ids = self.env['preventive.maintainence'].search(
            ['|', ('contract_id', '=', False),
             ('contract_product_id', '=', False)])
        for pm in pm_ids:
            contract_id = self.env['contract.contract'].search(
                [('iq', '=', pm.iq)])
            if len(contract_id.ids) == 1:
                pm.contract_id = contract_id.id
                contract_product_id = self.env['contract.product'].search(
                    [('sn', '=', pm.sn), ('sn', '!=', 0),
                     ('modality', '=', pm.modality.id),
                     ('contract_id.iq', '=', pm.iq),
                     ('starting_date', '=', pm.starting_date),
                     ('eoc_date', '=', pm.eoc_date)
                     ])
                pm.contract_product_id = contract_product_id.id
            else:
                pass

    def compute_is_pm_date_in_this_month_or_next_month(self):
        """ Scheduled action to compute the preventive maintenance lines is in this month or next month."""

        pm = self.env['preventive.maintainence'].search([])
        for line in pm:
            for rec in line.pm_date_lines:
                if rec.date.month == datetime.datetime.today().month and rec.date.year == datetime.datetime.today().year:
                    line.this_month = True
                    break
                else:
                    line.this_month = False

            for rec in line.pm_date_lines:
                if rec.date.month == (
                        datetime.datetime.today().month + 1) and rec.date.year == datetime.datetime.today().year:
                    line.next_month = True
                    break
                else:
                    line.next_month = False

    @api.depends('sn', 'iq')
    def compute_modality(self):
        """ Method to compute the modality of a preventive maintenance"""
        for rec in self:
            contract_ids = self.env['contract.contract'].search(
                [('iq', '=', rec.iq)])
            if contract_ids:
                for contract in contract_ids:
                    for contract_prdct in contract.product_lines:
                        if contract_prdct.sn == rec.sn:
                            rec.modality = contract_prdct.modality.id
                            break
                        else:
                            rec.modality = False

    def search_sn(self):
        """ Method to search serial number and find contract product lines based on it. """
        if not self.sn:
            raise UserError(
                _("Please fill in Serial Number before clicking Search"))

        product_ids = self.env['contract.product'].search(
            [('sn', '=ilike', self.sn)], order="starting_date")

        if len(product_ids) == 0:
            raise UserError(
                _(f"No Conrtact was found with for serial number {self.sn}"))
        if len(product_ids) == 1:
            self.modality = product_ids.modality
            self.starting_date = product_ids.starting_date
            self.eoc_date = product_ids.eoc_date
            self.iq = product_ids.contract_id.iq
            self.total_no_of_years = product_ids.warranty + product_ids.maintainence
            self.contract_id = product_ids.contract_id
            self.contract_product_id= product_ids.id
        if len(product_ids) > 1:
            self.modality = product_ids[-1].modality
            self.starting_date = product_ids[-1].starting_date
            self.eoc_date = product_ids[-1].eoc_date
            self.iq = product_ids[-1].contract_id.iq
            self.total_no_of_years = product_ids[-1].warranty + product_ids[
                -1].maintainence
            self.contract_id = product_ids[-1].contract_id
            self.contract_product_id = product_ids[-1].id

    def generate_dates_table(self):
        """ Method to generate preventive maintenance date lines . """
        list_of_dates = []
        final_date = self.eoc_date if self.ref == "eoc" else (
                self.starting_date + dateutil.relativedelta.relativedelta(
            years=self.service_years))
        if final_date and self.starting_date:
            no_of_days = final_date - self.starting_date
        else:
            no_of_days = 0
        loop = (
                       self.eoc_date - self.starting_date).days / 30 if self.ref == "manual" else no_of_days.days if no_of_days != 0 else no_of_days / 30  # Number of increments
        """ if eoc date is before PAC date """
        if loop < 0:
            raise UserError(_("EOC date can`t be before PAC Date"))

        """ first index of loop, list_of_dates is empty, this only happens one time, 
        then It will take the last element in list and increment it """
        # end_date = self.starting_date + relativedelta(years=self.total_no_of_years)
        if self.starting_date:
            st_dt = self.starting_date
            for i in range(0, self.total_no_of_years):
                year = i + 1
                end_date_of_the_yr = st_dt + relativedelta(years=year)
                iterations = int(12 / int(self.interval))
                for j in range(0, iterations):
                    inc = j + 1
                    new_date = st_dt + relativedelta(
                        months=(inc * (int(self.interval))))
                    if new_date <= end_date_of_the_yr:
                        list_of_dates.append({'new_date': new_date,
                                              'year': year,
                                              'pm_count': inc})
                    else:
                        break
                st_dt = self.starting_date + relativedelta(years=year)

        self.write({"pm_date_lines": [(5, 0)]})
        for item in list_of_dates:
            avoid_off_days = self.env['ir.config_parameter'].sudo().get_param(
                'helpdesk.avoid_off_days')
            value = self.env['ir.config_parameter'].sudo().get_param(
                'helpdesk.days_offset')
            if int(value) < 0:
                temp_date = item['new_date'] - datetime.timedelta(
                    days=abs(int(value)))
                if avoid_off_days:
                    if temp_date.strftime(
                            '%A') == 'Saturday' or temp_date.strftime(
                            '%A') == 'Friday':
                        temp_date = temp_date - datetime.timedelta(days=1)
                        if temp_date.strftime(
                                '%A') == 'Saturday' or temp_date.strftime(
                                '%A') == 'Friday':
                            temp_date = temp_date - datetime.timedelta(days=1)
            else:
                temp_date = item['new_date'] + datetime.timedelta(
                    days=abs(int(value)))
                if avoid_off_days:
                    if temp_date.strftime(
                            '%A') == 'Saturday' or temp_date.strftime(
                            '%A') == 'Friday':
                        temp_date = temp_date + datetime.timedelta(days=1)
                        if temp_date.strftime(
                                '%A') == 'Saturday' or temp_date.strftime(
                                '%A') == 'Friday':
                            temp_date = temp_date + datetime.timedelta(days=1)

            self.write({"pm_date_lines": [
                (0, 0,
                 {"date": item['new_date'], "year_count": item['year'],
                  "pm_count": item['pm_count'], "is_done": False,
                  "pm_rounded_date": temp_date if temp_date else False})]})

    def _pm_watch(self):
        """ Scheduled action to create preventive maintenance tickets from preventive maintenance date lines."""
        preventive_maintenance_ids = self.env["preventive.maintainence"].search(
            [("status", "=", "active")])
        for rec in preventive_maintenance_ids:
            preventive_maintainence_dates_ids = self.env[
                "preventive.maintainence.dates"].search(
                [("is_done", "=", False), ('pm_id', '=', rec.id)])
            dates = preventive_maintainence_dates_ids.mapped('date')
            years = []
            for date in dates:
                if date.year not in years:
                    years.append(date.year)

            if preventive_maintainence_dates_ids:
                for year in years:
                    for item in preventive_maintainence_dates_ids:
                        if year == item.date.year:
                            if item.is_done:
                                pass
                            else:
                                if item.pm_rounded_date:
                                    creation_date = item.pm_rounded_date - datetime.timedelta(
                                        days=item.pm_id.interval_days)
                                    if creation_date == datetime.date.today():
                                        if item.date == item.pm_id.eoc_date:
                                            text = "Final preventive maintenance done."
                                        else:
                                            number = num2words(item.pm_count,
                                                               to='ordinal')
                                            yearcount = item.year_count
                                            year_in_words = num2words(yearcount,
                                                                      to='ordinal')
                                            text = number + " preventive maintenanace done for the " + year_in_words + " year."
                                        helpdesk_ticket_id = self.env[
                                            "helpdesk.ticket"].create(
                                            {"sn_search": item.pm_id.sn,
                                             "pm_id": item.pm_id.id,
                                             'ticket_type_id': self.env[
                                                 'helpdesk.ticket.type'].search(
                                                 [('name', '=',
                                                   'Preventive maintenance')]).id,
                                             'stage_id': self.env[
                                                 'helpdesk.stage'].search(
                                                 [('name', '=', 'Assignment')],
                                                 limit=1).id,
                                             'pm_workdone_description': text,
                                             })
                                        helpdesk_ticket_id.search_by_sn()
                                        users = [user.id for user in
                                                 helpdesk_ticket_id.brand_id.user_ids]
                                        note = _(
                                            "A new ticket has been moved to your stage: %s") % (
                                                   helpdesk_ticket_id.stage_id.name)
                                        for user in users:
                                            helpdesk_ticket_id.activity_schedule(
                                                'custom_helpdesk.mail_activity_helpdesk_ticket_assigned',
                                                note=note,
                                                user_id=user)
                                        item.pm_id.message_post(
                                            body=f"A new helpdesk ticket was created at {datetime.datetime.today()}, Ticket id : {helpdesk_ticket_id.id}, Line Id : {item.id}")
                                        item.is_done = True
                                    else:
                                        pass
            else:
                pass


class CustomPreventiveMaintainenceDates(models.Model):
    """ Inherits preventive maintainence dates"""
    _inherit = 'preventive.maintainence.dates'

    pm_rounded_date = fields.Date(string="PM Rounded Date")
    year_count = fields.Integer(string="Year count")
    pm_count = fields.Integer(string="PM count")

    @api.onchange('date')
    def onchange_date(self):
        avoid_off_days = self.env['ir.config_parameter'].sudo().get_param(
            'helpdesk.avoid_off_days')
        value = self.env['ir.config_parameter'].sudo().get_param(
            'helpdesk.days_offset')
        if avoid_off_days:
            if self.date:
                temp_date = self.date
                index = int(value)
                if index > 0:
                    counter = 0
                    while 1:
                        if counter == index:
                            break
                        else:
                            temp_date = temp_date + datetime.timedelta(days=1)

                            if temp_date.strftime(
                                    '%A') == 'Saturday' or temp_date.strftime(
                                    '%A') == 'Friday':
                                pass
                            else:
                                counter = counter + 1
                    self.pm_rounded_date = temp_date
                else:
                    counter = 0
                    while 1:
                        if counter == abs(index):
                            break
                        else:
                            temp_date = temp_date - datetime.timedelta(days=1)
                            if temp_date.strftime(
                                    '%A') == 'Saturday' or temp_date.strftime(
                                    '%A') == 'Friday':
                                pass
                            else:
                                counter = counter + 1
                    self.pm_rounded_date = temp_date
            else:
                pass
        else:
            self.pm_rounded_date = self.date + datetime.timedelta(
                days=int(value))

    def create_pm_ticket(self):
        """ Method to create preventive maintenance ticket for the preventive maintenance dates lines."""
        if self.is_done:
            raise UserError(_("PM ticket is already generated."))
        else:
            dates = self.pm_id.pm_date_lines.mapped('date')
            years = []
            for date in dates:
                if date.year not in years:
                    years.append(date.year)

            pm_dates_lines = self.pm_id.pm_date_lines.filtered(
                (lambda rec: rec.date.year == self.date.year))
            pm_date_line_index = pm_dates_lines.browse(self.id)
            number = num2words(pm_date_line_index.pm_count, to='ordinal')
            yearcount = pm_date_line_index.year_count
            if pm_date_line_index.pm_id.eoc_date == pm_date_line_index.date:
                text = "Final preventive maintenance done."
            else:
                year_in_words = num2words(yearcount, to='ordinal')
                text = number + " preventive maintenance done for the " + year_in_words + " year."
            helpdesk_ticket_id = self.env["helpdesk.ticket"].create(
                {"sn_search": self.pm_id.sn,
                 "pm_id": self.pm_id.id,
                 'ticket_type_id': self.env['helpdesk.ticket.type'].search(
                     [('name', '=', 'Preventive maintenance')]).id,
                 'stage_id': self.env['helpdesk.stage'].search(
                     [('name', '=', 'Assignment')],
                     limit=1).id,
                 'pm_workdone_description': text,
                 })
            helpdesk_ticket_id.search_by_sn()
            users = [user.id for user in helpdesk_ticket_id.brand_id.user_ids]
            note = _("A new ticket has been moved to your stage: %s") % (
                helpdesk_ticket_id.stage_id.name)
            for user in users:
                helpdesk_ticket_id.activity_schedule(
                    'custom_helpdesk.mail_activity_helpdesk_ticket_assigned',
                    note=note,
                    user_id=user)
            self.pm_id.message_post(
                body=f"A new helpdesk ticket was created at {datetime.datetime.today()}, Ticket id : {helpdesk_ticket_id.id}, Line Id : {self.id}")
            self.is_done = True
