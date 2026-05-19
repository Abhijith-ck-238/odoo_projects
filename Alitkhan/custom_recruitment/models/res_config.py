from odoo import models, fields, api


class ConfSetting(models.TransientModel):
   _inherit = "res.config.settings"

   is_fields_visible = fields.Boolean(string="Show Hidden Fields", config_parameter='custom_recruitment.is_fields_visible')

   def get_values(self):
      res = super(ConfSetting, self).get_values()
      res.update(
         is_fields_visible=self.env['ir.config_parameter'].sudo().get_param(
            'custom_recruitment.is_fields_visible'),
      )
      return res

   def set_values(self):
      res = super(ConfSetting, self).set_values()
      self.env['ir.config_parameter'].sudo().set_param('custom_recruitment.is_fields_visible',
                                                       self.is_fields_visible)
      return res

   @api.onchange('is_fields_visible')
   def onchange_is_fields_visible(self):
       applications = self.env['hr.applicant'].search([])
       applications.write({
           'is_fields_visible': self.is_fields_visible
       })
