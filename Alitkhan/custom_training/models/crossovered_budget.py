from odoo import fields, models, api

class CrossoveredBudget(models.Model):
    _inherit = 'budget.analytic'

    training_id = fields.Many2one('training.ticket')

    @api.model
    def create(self,vals):
        res = super(CrossoveredBudget, self).create(vals)
        if vals.get('training_id'):
            approvres = self.env['ir.config_parameter'].sudo().get_param(
                'custom_training.budget_approvers')
            users = approvres.translate(
                {ord(c): None for c in "[]"})

            li = list(users.split(","))
            for user in li:
                self.env['mail.activity'].sudo().create({
                    'display_name': 'Budget Approval',
                    'summary': 'Budget Approval',
                    'note': 'Your approval is required for the training budget ' + res.name + '.',
                    'date_deadline': fields.datetime.now(),
                    'user_id': int(user),
                    'res_id': res.id,
                    'res_model_id': self.env['ir.model'].sudo().search(
                        [('model', '=', 'crossovered.budget')], limit=1).id,
                    'activity_type_id': self.env['mail.activity.type'].search(
                        [('name', 'like', 'Reminder for Training Budget Approval')], limit=1).id,
                })
        return res

    def action_budget_confirm(self):
        res = super(CrossoveredBudget, self).action_budget_validate()
        activities = self.activity_ids.ids
        self.env['mail.activity'].search([('id', 'in',activities), ('display_name','=', 'Budget Approval')]).action_done()
        return res
