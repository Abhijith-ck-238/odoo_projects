from ast import literal_eval

from odoo import fields, models


class ConfSetting(models.TransientModel):
   _inherit = "res.config.settings"

   limited_currency_ids = fields.Many2many('res.currency',string="Limited Currencies",
                                       relation="accounting_currency_limited_rel",
                                       column1="config_id",
                                       column2="currency_id",
                                       doamin="[('active', '=', True)]")
   budget_reminder_user_ids = fields.Many2many('res.users', string="Budget Reminder Users", relation="budget_reminder_user_rel")

   def get_values(self):
      res = super(ConfSetting, self).get_values()
      limited_currency_ids = self.env['ir.config_parameter'].sudo().get_param(
         'custom_expense.limited_currency_ids')
      budget_reminder_user_ids = self.env['ir.config_parameter'].sudo().get_param(
         'custom_expense.budget_reminder_user_ids')
      if limited_currency_ids:
         res.update({
            'limited_currency_ids': [(6, 0, literal_eval(
               limited_currency_ids) if limited_currency_ids else False)]
         })
      if budget_reminder_user_ids:
         res.update({
            'budget_reminder_user_ids': [(6, 0, literal_eval(budget_reminder_user_ids) if budget_reminder_user_ids else False)]
         })
      return res

   def set_values(self):
      res = super(ConfSetting, self).set_values()
      self.env['ir.config_parameter'].sudo().set_param(
         'custom_expense.limited_currency_ids', self.limited_currency_ids.ids)
      self.env['ir.config_parameter'].sudo().set_param(
         'custom_expense.budget_reminder_user_ids',
         self.budget_reminder_user_ids.ids)
      return res
