from odoo import models, fields, api
from ast import literal_eval


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    restored_date = fields.Datetime(string="Restored Day")
    force_edit_old_data = fields.Boolean(string="Force edit old data")

    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        restored_date = self.env['ir.config_parameter'].sudo().get_param(
            'hr_expense_advance_clear.restored_date')
        force_edit_old_data = self.env['ir.config_parameter'].sudo().get_param(
            'hr_expense_advance_clear.force_edit_old_data')
        res.update(
            restored_date=restored_date,
            force_edit_old_data=force_edit_old_data,
        )

        return res

    def set_values(self):
        res = super(ResConfigSettings, self).set_values()
        self.env['ir.config_parameter'].set_param('hr_expense_advance_clear.restored_date',
                                                  self.restored_date)
        self.env['ir.config_parameter'].set_param('hr_expense_advance_clear.force_edit_old_data',
                                                  self.force_edit_old_data)
        return res
