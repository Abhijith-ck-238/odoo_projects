# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError

class HelpdeskStage(models.Model):
    _inherit = "helpdesk.stage"

    modality_stage = fields.Boolean(string="Modality Stage", help="The stage where notifactions are send by modality instead of limited users field")
    limited_users = fields.Many2many('res.users', relation="ticket_to_users_rel", column1="users_col", column2="ticket_1_col")
    send_notification = fields.Boolean("Send Notifications", help="Send notifications to users in (Limited Users) field")
    only_notification = fields.Boolean("Only Notifications", help="Use the field of (Limited Users) to only send notification and not limit users")

    is_first = fields.Boolean("First Stage")
    cancelled_stage = fields.Boolean(string="Cancelled Stage")

    must_be_within_contract = fields.Boolean("Must be within contract", help="The support ticket must be within contract period\
         to be able to move the ticket directly from first ticket to this stage")

    must_be_out_of_contract = fields.Boolean("Must be out of contract", help="The support must be  out of contract period\
         to be able to move the ticket from first ticket to this stage")

    require_field_service = fields.Boolean(string="Require Service Report")
    auto_create_field_service = fields.Boolean(string="Auto Create Field Service Ticket")

    require_full_resource = fields.Boolean(string="Required Full Recources")

    only_valid_tickets = fields.Boolean("Only Valid Tickets")

    finished_fsm_ticket_stage = fields.Boolean("Finished Field Service Ticket Stage")

    @api.onchange("only_notification")
    def change_notificaion_settings(self):
         for rcd in self:
             if rcd.only_notification:
                   rcd.send_notification = True