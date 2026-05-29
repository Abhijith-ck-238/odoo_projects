from ast import literal_eval

from odoo import fields, models


class ConfSetting(models.TransientModel):
   _inherit = "res.config.settings"

   rfid_printer_name = fields.Char(string="RFID Printer", config_parameter='rfid_connector.rfid_printer_name')

   def get_values(self):
      res = super(ConfSetting, self).get_values()
      res.update(
         rfid_printer_name=self.env['ir.config_parameter'].sudo().get_param(
            'rfid_connector.rfid_printer_name')
      )
      return res

   def set_values(self):
      res = super(ConfSetting, self).set_values()
      self.env['ir.config_parameter'].sudo().set_param('rfid_connector.rfid_printer_name',
                                                       self.rfid_printer_name)
      return res