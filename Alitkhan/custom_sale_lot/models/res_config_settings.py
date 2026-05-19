from odoo import models, fields, api
from ast import literal_eval


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    confirm_activity_user_ids = fields.Many2many('res.users', 'sale_config_user_rel', 'config_id', 'uid',
                                                 string="Confirm Activity Users")
    lot_expiry_alert_user_ids = fields.Many2many('res.users', 'lot_expiry_user_rel', 'config_id', 'uid',
                                                 string="Lot Expiry Alert Users")

    def set_values(self):
        res = super(ResConfigSettings, self).set_values()
        self.env['ir.config_parameter'].sudo().set_param(
            'sale.confirm_activity_user_ids', self.confirm_activity_user_ids.ids)
        self.env['ir.config_parameter'].sudo().set_param(
            'sale.lot_expiry_alert_user_ids', self.lot_expiry_alert_user_ids.ids)
        return res

    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        users = self.env['ir.config_parameter'].sudo().get_param('sale.confirm_activity_user_ids')
        lot_users = self.env['ir.config_parameter'].sudo().get_param('sale.lot_expiry_alert_user_ids')
        res.update(
            confirm_activity_user_ids=[(6, 0, literal_eval(users))] if users else False,
            lot_expiry_alert_user_ids=[(6, 0, literal_eval(lot_users))] if lot_users else False)
        return res
