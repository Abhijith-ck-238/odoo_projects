# -*- coding: utf-8 -*-


from datetime import timedelta

from odoo import api, fields, models, tools, SUPERUSER_ID, _
from odoo.exceptions import UserError, AccessError, ValidationError
from odoo.tools.safe_eval import safe_eval
from odoo.tools.misc import format_date


class project_task(models.Model):
    _inherit = 'project.task'

    weight = fields.Integer(string='Weight')
    weight_percent_display = fields.Integer(compute='_fill_weight_percent_display', string=" ")
    max_rate = fields.Integer(default=100)

    @api.depends ('weight')
    def _fill_weight_percent_display(self):
        for rec in self:
            rec.weight_percent_display = rec.weight
    