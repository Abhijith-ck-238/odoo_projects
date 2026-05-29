# -*- coding: utf-8 -*-
from odoo import models, fields

class AccountAnalyticPlan(models.Model):
    _inherit = 'account.analytic.plan'

    active = fields.Boolean(default=True)
