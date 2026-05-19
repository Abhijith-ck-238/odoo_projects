# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError
import datetime, json


class HelpdeskTicketException(models.Model):
    _name = "helpdesk.ticket.exception"

    name = fields.Char()

class HelpDeskTicket(models.Model):
    _inherit = "helpdesk.ticket"
    
    CALL_TYPES = [("internal", "Internal"), ("customer","Customer")]
    
    # inherited fields
    name = fields.Char(readonly=True, default="New Ticket")
    partner_id = fields.Many2one(string="Reported By", tracking=True)
    partner_name = fields.Char(string="Reported By (Name)")
    partner_email = fields.Char(string="Reported By (E-mail)")
    ticket_type_id = fields.Many2one('helpdesk.ticket.type', string="Ticket Type")


    #Preventive Maintainence Link
    pm_id = fields.Many2one("preventive.maintainence")

    # new fields
    job_number = fields.Char(string="Job Number", readonly=True, copy=False)
    parent_ticket = fields.Many2one('helpdesk.ticket', readonly=True, copy=False)
    child_ticket = fields.Many2one('helpdesk.ticket', readonly=True, copy=False)
    recieve_date = fields.Datetime("Call Recieved Date", tracking=True)
    province_id = fields.Many2one('contract.province', string="Province", tracking=True)
    site_id = fields.Many2one('contract.site', string="Site", domain="[('site_province', '=', province_id)]", tracking=True)
    brand_id = fields.Many2one('contract.modality', string="Modality", tracking=True)
    unit_id = fields.Many2one('contract.product', string="Unit", domain="[('site', '=', site_id), ('modality' ,'=',brand_id)]", tracking=True)
    unit_eoc_date = fields.Date(related="unit_id.eoc_date", string="Contract Expiration Date")
    contract_is_valid = fields.Boolean(compute="_check_eoc_date")
    sn = fields.Char("SN Number", related="unit_id.sn")
    sn_search= fields.Char("Search By Serial Number")
    contract_id = fields.Many2one("contract.contract", string="Contract", related="unit_id.contract_id") # Shows related contract, Only one entry since SN never duplicate
    service_report_id = fields.Many2one("service.report", string="Service Report Ticket", readonly=True) # shows related service reports after reaching SN
    field_service_id = fields.Many2one("project.task", string="Field Services", readonly=True)
    call_type = fields.Selection(CALL_TYPES,string="Call type")
    call_number = fields.Char("Reported By (Phone Number)")
    exception_id = fields.Many2one("helpdesk.ticket.exception", string="Exception Reason")
    date_start = fields.Datetime(string="Starting Date")
    date_end = fields.Datetime(string="Ending Date")
    resource_overlap = fields.Boolean(compute="check_resource_overlap")
    overlap_string = fields.Char(compute="check_resource_overlap")
    overlap_sn = fields.Boolean(compute="compute_overlap_sn")
    resource_lines = fields.One2many("helpdedesk.resource", "helpdesk_ticket_id", string="Recources", default=lambda self: self._get_default_resource() )
    resources_are_full = fields.Boolean(compute="_check_resources")
    resource_json = fields.Text(compute="_gen_resource")
    description = fields.Text(required=True)
    
    @api.constrains("brand_id", "unit_id")
    def gen_name_field(self):
        for ticket in self:
            if ticket.brand_id:
                ticket.name = ticket.brand_id.name
                if ticket.unit_id:
                    ticket.name += ' - ' + ticket.unit_id.name

    @api.depends('unit_id')
    def compute_overlap_sn(self):
        for ticket in self:
            if ticket.unit_id:
                similiar_tickets = self.env['helpdesk.ticket'].search([('unit_id', '=' , ticket.unit_id.id)])
                if len(similiar_tickets) > 1:
                    ticket.overlap_sn = True
                else:
                    ticket.overlap_sn = False
            else:
                ticket.overlap_sn = False

    def create_sub_ticket(self):
        context = dict(self.env.context)
        context['default_job_number'] = self.job_number
        context['default_parent_ticket'] = self.id
        context['default_partner_id'] = self.partner_id.id
        context['default_ticket_type_id'] = self.ticket_type_id.id
        context['default_recieve_date'] = self.recieve_date
        context['default_call_type'] = self.call_type
        context['default_province_id'] = self.province_id.id
        context['default_site_id'] = self.site_id.id
        context['default_brand_id'] = self.brand_id.id
        context['default_unit_id'] = self.unit_id.id
        context['default_description'] = self.description
        return {
            "name": "Sub Ticket",
            "type": "ir.actions.act_window",
            "res_model": "helpdesk.ticket",
            "views": [[False, "form"]],
            "context": context,
            "res_id": False,
            "target": "current",
        }

    def _get_default_resource(self):
        return [
            (0, 0, { 'categ_id': self.env.ref('itkan_helpdesk.data_enginner'), 'qty': 0}),
            (0, 0, { 'categ_id': self.env.ref('itkan_helpdesk.data_co_enginner'), 'qty': 0}),
            (0, 0, { 'categ_id': self.env.ref('itkan_helpdesk.data_co_person'), 'qty': 0}),
            (0, 0, { 'categ_id': self.env.ref('itkan_helpdesk.data_technicians'), 'qty': 0}),
            (0, 0, { 'categ_id': self.env.ref('itkan_helpdesk.data_vehicles'), 'qty': 0}),
        ]

    @api.depends('date_start', 'date_end', 'resource_lines')
    def check_resource_overlap(self):
        for ticket in self:
            overlaped = ticket._check_resource_overlap()
            if overlaped:
                ticket.overlap_string = ', '.join( overlaped.mapped('display_name') )
                ticket.resource_overlap = True
            else:
                ticket.overlap_string = ''
                ticket.resource_overlap = False


    def _check_resource_overlap(self):
        for ticket in self:
            if ticket.date_start and ticket.date_end and (ticket.resource_lines or self.user_id) and type(ticket.id) == type( int() ):
                # getting all tickets within the same time range
                overlapped_tickets = self.env['helpdesk.ticket'].search([
                    ('active', '=', True),
                    ('id', '!=', ticket.id),
                    '|', 
                        ('user_id', '!=', False),
                        ('resource_lines', '!=', False),
                    '|',
                        '|',
                            '&',
                            ('date_start', '>=', ticket.date_start),
                            ('date_start', '<=', ticket.date_end),
                            '&',
                            ('date_end', '>=', ticket.date_start),
                            ('date_end', '<=', ticket.date_end),
                        '&',
                        ('date_start', '<=', ticket.date_start),
                        ('date_end', '>=', ticket.date_end),
                    ])
                if overlapped_tickets:
                    result = self.env['helpdesk.ticket']
                    for lapped_ticket in overlapped_tickets:
                        # check if the fetched ticket has the same user selected
                        lapped_users = lapped_ticket.resource_lines.mapped('user_ids.id')
                        if lapped_ticket.user_id:
                            lapped_users.append(lapped_ticket.user_id.id)

                        current_users = ticket.resource_lines.mapped('user_ids.id')
                        if ticket.user_id:
                            current_users.append(ticket.user_id.id)

                        overlapped_users = any(user for user in lapped_users if user in current_users)
                        if overlapped_users:
                            result += lapped_ticket
                        else:
                            pass

                    return result

                else:
                    return []

            else:
                return []

    @api.depends('resource_lines')
    def _gen_resource(self):
        for ticket in self:
            values = []
            for line in ticket.resource_lines:
                values.append({
                    'name': line.categ_id.name,
                    'categ_type': line.categ_type,
                    'qty': line.qty,
                    'remaining_qty': line.remaining_qty
                })
            ticket.resource_json = json.dumps(values) if values else []


    @api.depends('resource_lines')
    def _check_resources(self):
        for ticket in self:
            if ticket.resource_lines:
                for line in ticket.resource_lines:
                    if line.qty == len(line.user_ids) or line.qty == len(line.vehicle_ids):
                        ticket.resources_are_full = True
                    else:
                        ticket.resources_are_full = False
                        break
            else:
                ticket.resources_are_full = True

            

    @api.onchange('unit_eoc_date')
    def _check_eoc_date(self):
        for ticket in self:
            if ticket.unit_eoc_date and ticket.unit_eoc_date >= datetime.date.today():
                ticket.contract_is_valid = True
            else:
                ticket.contract_is_valid = False

    @api.onchange("site_id")
    def _compute_brand(self):
        res={}
        brands=[]
        rcds = self.env["contract.contract"].search([])
        for item in rcds:
            for product in item.product_lines:
                if product.site.id == self.site_id.id:
                    brands.append(product.modality.id)
        res['domain'] = {'brand_id': [("id", "in", brands)] }
        return res

    def search_by_sn(self):
        contract_line_id = self.env['contract.product'].search([('sn', 'like', self.sn_search )], order="starting_date desc", limit=1)
        # raise UserError( contract_line_id )
        if len(contract_line_id) == 0:
            raise UserError(_(f"No Conrtact was found with for serial number {self.sn_search}"))

        else:
            self.write({
                'unit_id':contract_line_id.id,
                'province_id':contract_line_id.site.site_province.id,
                'brand_id':contract_line_id.modality.id,
                'site_id':contract_line_id.site.id,
            })
            # self.unit_id = contract_line_id.id
            # self.province_id = contract_line_id.site.site_province.id
            # self.brand_id = contract_line_id.modality.id
            # self.site_id = contract_line_id.site.id

    @api.model
    def create(self, values):
        record = super(HelpDeskTicket, self).create(values)

        if not record.job_number:
            last_ticket = self.env['helpdesk.ticket'].search([('job_number', '!=', False)], order="job_number desc", limit=1)
            if last_ticket:
                number =  int(last_ticket.job_number[3:]) + 1
                new_job_number = 'JB-' + str(number).zfill(5)
                record.job_number = new_job_number
            else:
                record.job_number = "JB-00001"

        else:
            parent_ticket = record.parent_ticket
            parent_ticket.child_ticket = record.id
            if parent_ticket.field_service_id:
                project_task = parent_ticket.field_service_id
                task_done_stage = self.env['project.task.type'].search([('project_ids', '=', project_task.project_id.id), ('state', '=', 'done')])
                if len(task_done_stage) < 1:
                    raise UserError("Could not find a project stage that matches the requirments. Please contact your suppport")
                if len(task_done_stage) == 1:
                    project_task.stage_id = task_done_stage.id
                if len(task_done_stage) > 1:
                    raise UserError(f"Multiple done stages detected. please contact your supprt:\n{', '.join( task_done_stage.mapped('name') )}")

            ticket_done_stage = self.env['helpdesk.stage'].search([('cancelled_stage', '=', False), ('team_ids', 'in', parent_ticket.team_id.id)])
            if len(ticket_done_stage) < 1:
                raise UserError("Could not find a project stage that matches the requirments. Please contact your suppport")
            if len(ticket_done_stage) == 1:
                parent_ticket.stage_id = ticket_done_stage.id
            if len(ticket_done_stage) > 1:
                raise UserError(f"Multiple done stages detected. please contact your supprt:\n{', '.join( ticket_done_stage.mapped('name') )}")

        return record


    def write(self, values):
        if values.get('stage_id'):

            new_stage_id = self.env['helpdesk.stage'].browse([ values['stage_id'] ])
            # this section is to allow moving tickets forward only
            if self.stage_id.sequence > new_stage_id.sequence:
                raise UserError(_("You can only move tickets forward"))
            else:
                # === ALLOW ===
                pass

            # this section is to check whether the user have the premission of moving from the selected ticket
            if self.stage_id.limited_users and not self.stage_id.only_notification:
                if self.env.user.id in self.stage_id.limited_users.ids:
                    # === ALLOW ===
                    pass

                else:
                    raise UserError(_("You don't have premission to move the ticket to this stage"))

            else:
                # === ALLOW ===
                pass
            
            # this section is to check whether the new stage must be within contract
            if new_stage_id.must_be_within_contract and self.stage_id.is_first and not self.exception_id:
                if self.unit_id and self.contract_is_valid:
                    # === ALLOW ===
                    pass

                else:
                    raise UserError(_(f"You can not  move this ticket directly to the {new_stage_id.name} stage cause it is not within contract"))
            
            # this section is to check whether the new stage must be out of contract
            if new_stage_id.must_be_out_of_contract and self.stage_id.is_first and not self.exception_id:
                if self.unit_id and self.contract_is_valid:
                    raise UserError(_(f"This ticket can not be moved to {new_stage_id.name} stage because it's already within contract"))

                else:
                    # === ALLOW ===
                    pass

            # this section is to check whether the new stage require full resources
            if new_stage_id.require_full_resource and not self.resources_are_full:
                raise UserError(_(f"This ticket can not be moved to {new_stage_id.name} stage because some resources are missing"))

            else:
                # === ALLOW ===
                pass

        return super(HelpDeskTicket, self).write(values)
            
    @api.constrains('stage_id')
    def check_stage_service(self):
        for ticket in self:
            # Check if Service Report Was Created Before Moving to a stage that required service report
            if ticket.stage_id.require_field_service and not ticket.field_service_id.service_report_id:
                raise UserError(_("The field service ticket needs to finish its cycle before moving this helpdeks ticket"))

            co_workers = [(4, user.id) for user in ticket.resource_lines.mapped('user_ids')]
            co_vehicles = [(4, vehicle.id) for vehicle in ticket.resource_lines.mapped('vehicle_ids')]
            # Auto create service report if the ticket is moved to an auto_create_field_service stage
            if ticket.stage_id.auto_create_field_service:
                if ticket.date_start and ticket.date_end and ticket.user_id and ticket.partner_id:
                    project_id = self.env.ref('industry_fsm.fsm_project')
                    service_id  = self.env['project.task'].create({
                        "name": f"FS - {ticket.name}",
                        "brand_id": ticket.brand_id.id,
                        "co_user_ids": co_workers,
                        "vehicle_ids": co_vehicles,
                        "planned_date_begin": ticket.date_start,
                        "date_deadline": ticket.date_end,
                        "is_fsm": True,
                        "description": ticket.description,
                        "user_ids": [(4,ticket.user_id.id)],
                        "project_id": project_id.id,
                        "partner_id": ticket.partner_id.id,
                        "related_helpdesk_ticket": ticket.id,
                        })
                    ticket.field_service_id = service_id.id
                elif not ticket.partner_id:
                    raise UserError( _("Please enter the \"Report By\" Person") )
                elif not ticket.user_id:
                    raise UserError( _("Please select the reponsible user before moving the ticket") )
                else:
                    raise UserError( _("Please fill the task range before moving the ticket") )

    @api.constrains('stage_id')
    def send_users_notificaiton(self):
        users = False
        if self.stage_id.modality_stage:
            modality_id = self.unit_id.modality
            users = [user.partner_id.id for user in modality_id.user_ids]

        elif self.stage_id.limited_users and self.stage_id.send_notification and not (self.stage_id.only_valid_tickets and not self.contract_is_valid):
            users = [user.partner_id.id for user in self.stage_id.limited_users]

        #=============================

        if users:
            self.message_post(
                body= f"A new ticket has been moved to your stage:<br/>{self.display_name}",
                message_type='notification',
                subtype_xmlid='mail.mt_comment',
                partner_ids= users)

        else:
            pass

    def view_overlapped_tickets(self):
        lapped_tickets = self._check_resource_overlap()
        if lapped_tickets:

            return {
                'type': 'ir.actions.act_window',
                'name': 'Overlapped Ticket',
                'view_type': 'form',
                'view_mode': 'kanban',
                'res_model': 'helpdesk.ticket',
                'views': [(False,'kanban'), (False, 'list'), (False, 'form')],
                'domain': [( 'id', 'in', lapped_tickets.ids )],
                'target': 'current'
            }

        else:
            pass


    def view_field_service(self):
        if self.field_service_id:
            # view_id = self.env.ref('industry_fsm.project_task_view_form')
            view_id = self.env.ref('industry_fsm.view_task_form2_inherit')
            return {
                "name": "Field Service Ticket",
                "type": "ir.actions.act_window",
                "res_model": "project.task",
                "views": [[ view_id.id , "form"]],
                "res_id": self.field_service_id.id,
            }
        else:
            pass

    def view_service_report(self):
        if self.service_report_id:
            return {
                "name": "Service Report",
                "type": "ir.actions.act_window",
                "res_model": "service.report",
                "views": [[ False , "form"]],
                "res_id": self.service_report_id.id,
            }
        else:
            pass

    def view_parent_ticket(self):
        if self.parent_ticket:
            return {
                "name": "Parent Ticket",
                "type": "ir.actions.act_window",
                "res_model": "helpdesk.ticket",
                "views": [[ False , "form"]],
                "res_id": self.parent_ticket.id,
            }
        else:
            pass

    def view_child_ticket(self):
        if self.child_ticket:
            return {
                "name": "Child Ticket",
                "type": "ir.actions.act_window",
                "res_model": "helpdesk.ticket",
                "views": [[ False , "form"]],
                "res_id": self.child_ticket.id,
            }
        else:
            pass



    def return_check_resources_view(self):
        view_id = self.env.ref('project_enterprise.project_task_view_gantt')
        search_id = self.env.ref('industry_fsm.project_task_view_search_fsm')
        return {
            'name': 'Available Resources',
            'type': 'ir.actions.act_window',
            'view_mode': 'gantt',
            'res_model': 'project.task' ,   # name of respective model,
            'views': [(view_id.id, 'gantt')],
            'search_view_id': search_id.id,
            'domain': [('is_fsm', '=', True)],
            'context': {'search_default_groupby_user': 1, 'fsm_mode': 1, 'task_nameget_with_hours': 1},
            'target': 'new',
            }