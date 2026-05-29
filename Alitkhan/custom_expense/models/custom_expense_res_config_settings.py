# from ast import literal_eval
#
# from odoo import models, fields, api
#
#
# class CustomExpenseResConfigSettings(models.TransientModel):
#     _inherit = 'res.config.settings'
#
#     accounting_users_to_notify = fields.Many2many('res.users',
#                                                   string='Accounting Users to Notify',
#                                                   config_parameter='custom_expense.accounting_users_to_notify'
#                                                   )
#     budget_check_approver = fields.Many2many('res.users',
#                                              string="Approver of Budget Check", relation="rel_approver_budget",
#                                              config_parameter='custom_expense.budget_check_approver')
#
#     # @api.model
#     # def get_values(self):
#     #     res = super(CustomExpenseResConfigSettings, self).get_values()
#     #     accounting_user = self.env['ir.config_parameter'].sudo().get_param(
#     #         'custom_expense.accounting_users_to_notify')
#     #     budget_check_approver = self.env['ir.config_parameter'].sudo().get_param(
#     #         'custom_expense.budget_check_approver')
#     #     if accounting_user:
#     #         res.update({
#     #             'accounting_users_to_notify': [(6, 0, literal_eval(
#     #                 accounting_user) if accounting_user else False)]
#     #         })
#     #     if budget_check_approver:
#     #         res.update({
#     #             'budget_check_approver': [(6, 0, literal_eval(
#     #                 budget_check_approver) if budget_check_approver else False)]
#     #         })
#     #     return res
#     #
#     # def set_values(self):
#     #     res = super(CustomExpenseResConfigSettings, self).set_values()
#     #     self.env['ir.config_parameter'].set_param(
#     #         'custom_expense.accounting_users_to_notify',
#     #         self.accounting_users_to_notify.ids or False)
#     #     self.env['ir.config_parameter'].set_param(
#     #         'custom_expense.budget_check_approver',
#     #         self.budget_check_approver.ids or False)
#     #     return res


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

    # TODO: The below content is commented because it is not required in the latest database.The related functionality is no longer part of the current business process.Kept only for reference during migration and validation.


    # @api.model
    # def get_values(self):
    #     res = super(CustomExpenseResConfigSettings, self).get_values()
    #     accounting_user = self.env['ir.config_parameter'].sudo().get_param(
    #         'custom_expense.accounting_users_to_notify')
    #     budget_check_approver = self.env['ir.config_parameter'].sudo().get_param(
    #         'custom_expense.budget_check_approver')
    #     if accounting_user:
    #         res.update({
    #             'accounting_users_to_notify': [(6, 0, literal_eval(
    #                 accounting_user) if accounting_user else False)]
    #         })
    #     if budget_check_approver:
    #         res.update({
    #             'budget_check_approver': [(6, 0, literal_eval(
    #                 budget_check_approver) if budget_check_approver else False)]
    #         })
    #     return res
    #
    # def set_values(self):
    #     res = super(CustomExpenseResConfigSettings, self).set_values()
    #     self.env['ir.config_parameter'].set_param(
    #         'custom_expense.accounting_users_to_notify',
    #         self.accounting_users_to_notify.ids or False)
    #     self.env['ir.config_parameter'].set_param(
    #         'custom_expense.budget_check_approver',
    #         self.budget_check_approver.ids or []
    #     )
