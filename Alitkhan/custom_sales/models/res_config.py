from odoo import fields, models

class SaleConfSetting(models.TransientModel):
    _inherit = "res.config.settings"

    bnk_account_id = fields.Many2one('res.partner.bank',
                                      string="Bank Account",
                                      config_parameter='custom_sales.bnk_account_id')
