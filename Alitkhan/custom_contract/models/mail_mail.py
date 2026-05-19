from dataclasses import fields

# from odoo import api, models,fields
#
#
# class MailMail(models.Model):
#     _inherit = 'mail.mail'
#
#     channel_ids = fields.Many2many('discuss.channel')
#
#     @api.model
#     def create(self,vals):
#         res = super(MailMail,self).create(vals)
#         if res.channel_ids:
#             for channel in res.channel_ids:
#                 if channel.add_sender_to_cc:
#                     res.email_cc = self.env.user.login
#         return res