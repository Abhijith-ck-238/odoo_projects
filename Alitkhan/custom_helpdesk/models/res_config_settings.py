from odoo import models, fields, api
from ast import literal_eval


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    days_offset = fields.Integer(string="Days Offset")
    avoid_off_days = fields.Boolean(string="Avoid off Days")
    modality_ids = fields.Many2many("contract.modality", string='Modality')

    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        avoid_off_days = self.env['ir.config_parameter'].sudo().get_param(
            'helpdesk.avoid_off_days')
        days_offset = self.env['ir.config_parameter'].sudo().get_param(
            'helpdesk.days_offset')
        modality_ids = self.env["ir.config_parameter"].sudo().get_param('custom_helpdesk.modality_ids')
        res.update(
            avoid_off_days=avoid_off_days,
            days_offset=int(days_offset),
        )
        if modality_ids:
            res.update({
                'modality_ids': [(6, 0, literal_eval(
                    modality_ids) if modality_ids else False)]
            })
        return res

    def set_values(self):
        res = super(ResConfigSettings, self).set_values()
        self.env['ir.config_parameter'].set_param('helpdesk.avoid_off_days',
                                                  self.avoid_off_days)
        self.env['ir.config_parameter'].set_param('helpdesk.days_offset',
                                                  self.days_offset)
        self.env['ir.config_parameter'].sudo().set_param(
            'custom_helpdesk.modality_ids', self.modality_ids.ids)

        return res
