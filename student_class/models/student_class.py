from odoo import models, fields

class StudentClass(models.Model):
    _name = 'student.class'
    _description = 'Sample Model'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string='Student Name', required=True)
    description = fields.Text(string='Information')
    date = fields.Date(string='Start Date')
    active = fields.Boolean(string='Available', default=True)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirmed', 'Confirmed'),
        ('done', 'Done')
    ], string='Status', default='draft', tracking=True)
