# -*- coding: utf-8 -*-
from odoo import models, fields, api

class CalendarEventExt(models.Model):

    _inherit="calendar.event"

    do_not_notify = fields.Boolean(string="Do not send a notification")

    @api.model
    def create(self,vals):
        if vals.get('do_not_notify'):
           event = super(CalendarEventExt,self.with_context(mail_notrack=True)).create(vals)
           return event
            
        else:
            event = super(CalendarEventExt,self).create(vals)
            return event
