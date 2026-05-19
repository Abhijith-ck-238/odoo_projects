# -*- coding: utf-8 -*-
from odoo import fields, models


class AccountAnalyticPlan(models.Model):
    _inherit = 'account.analytic.plan'

    user_id = fields.Many2many('res.users', string='Owners')

class AnalyticAccountAccount(models.Model):
    _inherit = 'account.analytic.account'

    group_id = fields.Many2one('account.group', string='Group')
    initial_amount = fields.Float(string='Initial Budget Amount', compute="compute_initial_amount")


    def compute_initial_amount(self):
        for rec in self:
            amount = 0
            for line in rec.budget_line_ids:
                if line.crossovered_budget_id.sudo().date_from == line.date_from:
                    amount += line.budget_amount
            rec.initial_amount = amount
