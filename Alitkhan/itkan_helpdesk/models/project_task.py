# -*- coding: utf-8 -*-
from markupsafe import Markup

from odoo import models, fields, api, _
from odoo.exceptions import UserError
import datetime

class ProjectTaskExt(models.Model):

    _inherit="project.task"

    related_helpdesk_ticket = fields.Many2one("helpdesk.ticket", string="Related Helpdesk Ticket")
    brand_id = fields.Many2one('contract.modality', string="Modality")
    service_report_id = fields.Many2one("service.report", string="Service Reports", ondelete="cascade")
    co_user_ids = fields.Many2many('res.users', string="Co Person(s)", tracking=True, relation="project_task_res_users_rel_backup")
    event_ids = fields.Many2many('calendar.event', readonly=True)
    vehicle_ids = fields.Many2many('fleet.vehicle', string="Vehicles")
    service_report_doc = fields.Binary("Service Report Document")
    sale_order_id = fields.Many2one('sale.order', 'Sales Order', domain="[('partner_id', '=', partner_id)]", readonly=True, copy=False, help="Sales order to which the project is linked.")
    planned_date_end = fields.Datetime("End date")


    def action_fsm_view_material(self):
        res = super(ProjectTaskExt, self.sudo()).action_fsm_view_material()
        return res
    
    @api.constrains('planned_date_begin', 'planned_date_end')
    def _set_calander_event(self):
        if self.planned_date_begin and self.planned_date_end:
            self.event_ids.unlink()
            users = [user for user in self.co_user_ids]

            if self.user_ids:
                users.append(self.user_ids)

            # raise UserError( str(users) )
            for user_id in users:
                event = self.env['calendar.event'].create({
                    'name': self.name,
                    'send_email_to_attendees': True,
                    'start': self.planned_date_begin,
                    'stop': self.planned_date_end,
                    'partner_id': user_id.partner_id.id,
                    'user_id': user_id.id,
                    'partner_ids': [user_id.partner_id.id],
                    'privacy': 'confidential',
                })
                self.event_ids += event

    @api.constrains('co_user_ids')
    def send_notification_to_co_workers(self):
        if self.co_user_ids:
            users = [user.partner_id.id for user in self.co_user_ids]
            msg_body = ''
            for user in self.co_user_ids:
                msg_body += Markup(('<a href="#" data-oe-model="res.users" data-oe-id="%s">"%s"</a>, ')%(user.id,user.name))

            msg_body = msg_body[:-2]
            msg_body += '\nYou have been assigned the following task'

            self.message_post(
                body= msg_body,
                message_type='notification',
                subtype_xmlid='mail.mt_comment',
                partner_ids= users)

    @api.constrains('stage_id')
    def check_stage_change(self):
        # project_state = self.stage_id.state

        # creating service Report
        if self.stage_id.auto_create_service_report and self.is_fsm and self.related_helpdesk_ticket and not self.related_helpdesk_ticket.child_ticket and self.related_helpdesk_ticket.ticket_type_id.require_service_report:
            ticket_id = self.related_helpdesk_ticket
            cars_names = ticket_id.resource_lines.mapped('vehicle_ids.name')
            cars_sting = ', '.join(cars_names)
            service_report_id = self.env['service.report'].create({
                'task_number': '#' + str(ticket_id.id),
                'modality': ticket_id.brand_id.id,
                'province': ticket_id.province_id.id,
                't_type': 'job',
                'reported_by': ticket_id.site_id.site_name,
                'car': cars_sting,
                'contract': ticket_id.contract_id.id,
                'date': datetime.date.today(),
                'site': ticket_id.site_id.id,
                'sn': ticket_id.sn,
                'unit': ticket_id.unit_id.product_char if ticket_id.unit_id.product_char else ticket_id.unit_id.product_id.name,
            })

            self.service_report_id = service_report_id
            ticket_id.service_report_id = service_report_id

        # moving related helpdesk ticket to related stage
        if self.stage_id.helpdesk_stage_id and self.is_fsm and self.related_helpdesk_ticket and not self.related_helpdesk_ticket.child_ticket:
            ticket_id = self.related_helpdesk_ticket
            ticket_id.stage_id = self.stage_id.helpdesk_stage_id.id

        # sending notification
        if (self.stage_id.modality_stage and self.related_helpdesk_ticket) or (self.stage_id.limited_users):
            users = []
            modality_id = self.related_helpdesk_ticket.brand_id
            msg_body = 'Dear '

            if modality_id and modality_id.user_ids and self.stage_id.modality_stage:
                users = [user.partner_id.id for user in modality_id.user_ids]
                for user in modality_id.user_ids:
                    msg_body += Markup(('<a href="#" data-oe-model="res.users" data-oe-id="%s">"%s"</a>, ')(user.id,user.name))

            elif self.stage_id.limited_users:
                users = [user.partner_id.id for user in self.stage_id.limited_users]
                for user in self.stage_id.limited_users:
                    msg_body += Markup(('<a href="#" data-oe-model="res.users" data-oe-id="%s">"%s"</a>, ') %(user.id,user.name))

            # ==============================
            view_id = self.env.ref("industry_fsm.project_task_view_form")
            if users:
                msg_body = msg_body[:-2] + Markup((' A new fields service ticket is waiting for you approval:\
                     <a href="#" data-oe-model="project.task" data-oe-id="%s" data-oe-view="%s" data-oe-view-ref="%s" data-oe-view_ref="%s">"%s"</a>')%(self.id,view_id.id,view_id.id,view_id.id,self.display_name))
                self.message_post(
                    body= msg_body,
                    message_type='notification',
                    subtype_xmlid='mail.mt_comment',
                    partner_ids= users)

            else:
                pass

    def write(self, values):
        # checking if user has access
        # doing from here instead of from the record rule model because I had several issues
        field_service_manager_group = self.env.ref('industry_fsm.group_fsm_manager')
        for rec in self:
            if rec.is_fsm and not (values.get('related_helpdesk_ticket') or values.get('event_ids') )and self.env.user.id not in self.user_ids.ids and self.env.user.id not in field_service_manager_group.users.ids:
                raise UserError("You don't have premission to make changes to this task")

        old_stage = self.stage_id
        if values.get("stage_id") and self.related_helpdesk_ticket and not self.related_helpdesk_ticket.child_ticket and self.related_helpdesk_ticket.ticket_type_id.require_service_report:
            # checking if service report is required & uploaded
            new_stage = self.env['project.task.type'].browse([ values['stage_id'] ])
            if new_stage.require_service_report and not self.service_report_docs:
                raise UserError(_("You need to upload a service report document before moving the task to this stage"))

            if old_stage.modality_stage and self.related_helpdesk_ticket:
                modality_id = self.related_helpdesk_ticket.brand_id
                if modality_id and modality_id.user_ids:
                    if self.env.user.id not in modality_id.user_ids.ids:
                        raise UserError(_("You don't have access to move this task"))


            if old_stage.limited_users:
                if self.env.user.id not in old_stage.limited_users.ids:
                    raise UserError(_("You don't have access to move this task"))

        
        res = super(ProjectTaskExt, self).write(values)

        if values.get("stage_id") and self.stage_id.ticket_must_be_invalid and\
            self.related_helpdesk_ticket and self.related_helpdesk_ticket.contract_is_valid:
            raise UserError(_("You can not move a field service task to this stage because its related helpdesk ticket is still with-in contract"))

        return res

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
