from odoo import models, fields

class DiscussChannel(models.Model):
    _inherit = 'discuss.channel'

    crosspost_send_email = fields.Boolean(
        string="Send by Email",
        default=False, 
        help="If enabled, members of this channel will receive an email when this channel is mentioned in a chatter log."
    )
