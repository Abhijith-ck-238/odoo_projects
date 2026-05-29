from odoo import fields, models


class ItkanProjectConfSetting(models.TransientModel):
    _inherit = "res.config.settings"

    stage_id = fields.Many2one('project.stage',
                                      string="Deadline Stage",
                                      config_parameter='custom_itkan_project.stage_id')

    def get_values(self):
        res = super(ItkanProjectConfSetting, self).get_values()
        stage_id = int(self.env['ir.config_parameter'].sudo().get_param(
            'custom_itkan_project.stage_id'))
        if stage_id == 0:
               stage_id = False
        res.update(
               stage_id = stage_id,
        )
        return res

    def set_values(self):
        res = super(ItkanProjectConfSetting, self).set_values()
        self.env['ir.config_parameter'].sudo().set_param('custom_itkan_project.stage_id',
                                                          self.stage_id.id)
        return res

