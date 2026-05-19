from odoo import fields, models

class AttendeePosition(models.Model):
    _name = 'attendees.position'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = "Attendees Position"

    name = fields.Char(string="Name")

class WorkLocation(models.Model):
    _name = 'work.location'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = "Work Location"

    name = fields.Char(string="Name")

class SiteSector(models.Model):
    _name = 'site.sector'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = "Site Sector"

    name = fields.Char(string="Name")
