# -*- coding: utf-8 -*
from odoo import models


class IrHttp(models.AbstractModel):
    _inherit = 'ir.http'

    def session_info(self):
        res = super(IrHttp, self).session_info()
        res['rfid_printer_name'] = self.env['ir.config_parameter'].sudo().get_param('rfid_connector.rfid_printer_name')
        return res