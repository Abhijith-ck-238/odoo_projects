from odoo import fields,models


class MailChannel(models.Model):
    _inherit = 'discuss.channel'

    add_sender_to_cc = fields.Boolean(string="Add Sender to CC")
