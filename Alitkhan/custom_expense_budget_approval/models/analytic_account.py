# -*- coding: utf-8 -*-
from odoo import api, fields, models


class AnalyticAccount(models.Model):
    """ This model represents analytic.account."""
    _name = 'analytic.account'
    _description = 'AnalyticAccount'

    journal_id = fields.Many2one('account.journal', "Expense Journal")
