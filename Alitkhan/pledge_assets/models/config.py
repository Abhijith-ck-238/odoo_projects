from odoo import models, fields, api


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    pt = fields.Integer(
        string="Notify x days before expiration of pledge",
        config_parameter='pledge_assets.pt',
    )

    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        res.update(
            pt=int( self.env['ir.config_parameter'].sudo().get_param('pledge_assets.pt'))
        )
        return res


    def set_values(self):
        super(ResConfigSettings, self).set_values()
        self.env['ir.config_parameter'].sudo().set_param('pledge_assets.pt', int(self.pt))
