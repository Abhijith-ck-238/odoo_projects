# -*- coding: utf-8 -*-
from odoo import models, fields, api
from ast import literal_eval

class CustomExpenseResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    accounting_users_to_notify = fields.Many2many(
        'res.users',
        string='Accounting Users to Notify'
    )
    budget_check_approver = fields.Many2many(
        'res.users',
        string="Approver of Budget Check",
        relation="rel_approver_budget"
    )
    limited_currency_ids = fields.Many2many('res.currency', string="Limited Currencies",
                                            relation="accounting_currency_limited_rel",
                                            column1="config_id",
                                            column2="currency_id",
                                            domain="[('active', '=', True)]")
    budget_reminder_user_ids = fields.Many2many('res.users', string="Budget Reminder Users",
                                                relation="budget_reminder_user_rel")

    @api.model
    def get_values(self):
        res = super(CustomExpenseResConfigSettings, self).get_values()
        accounting_user = self.env['ir.config_parameter'].sudo().get_param(
            'custom_expense.accounting_users_to_notify')
        budget_check_approver = self.env['ir.config_parameter'].sudo().get_param(
            'custom_expense.budget_check_approver')
        limited_currency_ids = self.env['ir.config_parameter'].sudo().get_param(
            'custom_expense.limited_currency_ids')
        budget_reminder_user_ids = self.env['ir.config_parameter'].sudo().get_param(
            'custom_expense.budget_reminder_user_ids')
        if accounting_user:
            res.update({
                'accounting_users_to_notify': [(6, 0, literal_eval(
                    accounting_user))]
            })
        if budget_check_approver:
            res.update({
                'budget_check_approver': [(6, 0, literal_eval(
                    budget_check_approver))]
            })
        if limited_currency_ids:
            res.update({
                'limited_currency_ids': [(6, 0, literal_eval(
                    limited_currency_ids))]
            })
        if budget_reminder_user_ids:
            res.update({
                'budget_reminder_user_ids': [
                    (6, 0, literal_eval(budget_reminder_user_ids))]
            })
        return res

    def set_values(self):
        res = super(CustomExpenseResConfigSettings, self).set_values()
        self.env['ir.config_parameter'].set_param(
            'custom_expense.accounting_users_to_notify',
            self.accounting_users_to_notify.ids or False)
        self.env['ir.config_parameter'].set_param(
            'custom_expense.budget_check_approver',
            self.budget_check_approver.ids or []
        )
        self.env['ir.config_parameter'].sudo().set_param(
            'custom_expense.limited_currency_ids', self.limited_currency_ids.ids)
        self.env['ir.config_parameter'].sudo().set_param(
            'custom_expense.budget_reminder_user_ids',
            self.budget_reminder_user_ids.ids)
        return res
