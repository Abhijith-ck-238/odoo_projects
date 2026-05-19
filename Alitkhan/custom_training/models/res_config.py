from ast import literal_eval

from odoo import api, fields, models


class ConfSetting(models.TransientModel):
   _inherit = "res.config.settings"

   send_reminder = fields.Boolean(string="Reminder for due date", config_parameter='custom_training.send_reminder')
   days_to_remind = fields.Integer(string="Days", store=True, config_parameter="custom_training.days_to_remind")
   budget_approvers = fields.Many2many('res.users',string="Budget Approvers",
                                       relation="training_budget_users_rel",
                                       column1="config_id",
                                       column2="user_id"
                                       )
   def get_values(self):
      res = super(ConfSetting, self).get_values()
      budget_approvers = self.env['ir.config_parameter'].sudo().get_param(
         'custom_training.budget_approvers')
      res.update(
         send_reminder=self.env['ir.config_parameter'].sudo().get_param(
            'custom_training.send_reminder'),
         days_to_remind = int(self.env['ir.config_parameter'].sudo().get_param(
            'custom_training.days_to_remind')),
      )
      if budget_approvers:
         res.update({
            'budget_approvers': [(6, 0, literal_eval(
               budget_approvers) if budget_approvers else False)]
         })
      return res

   def set_values(self):
      res = super(ConfSetting, self).set_values()
      self.env['ir.config_parameter'].sudo().set_param('custom_training.send_reminder',
                                                       self.send_reminder)
      self.env['ir.config_parameter'].sudo().set_param(
         'custom_training.days_to_remind', int(self.days_to_remind))
      self.env['ir.config_parameter'].sudo().set_param(
         'custom_training.budget_approvers', self.budget_approvers.ids)
      return res

