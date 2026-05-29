from odoo import models, fields, api
from odoo.exceptions import UserError
from odoo.tools.translate import _
import datetime


class HrRecruitmentStage(models.Model):
    _inherit = "hr.recruitment.stage"

    is_interview = fields.Boolean("Is Interview ?")
    is_accepted = fields.Boolean("Is Accepted ?")

    @api.constrains('is_accepted')
    def _check_is_accepted(self):
        is_accepted = self.env['hr.recruitment.stage'].search([
            ('is_accepted', '=', True),
        ])
        if len(is_accepted) > 1:
            raise UserError(
                _("Only one stage can be an accepted stage."))
