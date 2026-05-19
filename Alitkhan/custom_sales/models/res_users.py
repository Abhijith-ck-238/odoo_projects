from odoo import models, fields, api

class CustomResUsers(models.Model):
    _inherit = 'res.users'

    emp_id = fields.Many2one('hr.employee', string="Employee", store=True,
                             compute='_compute_company_emp_id')

    @api.depends('employee_ids')
    @api.depends_context('force_company')
    def _compute_company_emp_id(self):
        for user in self:
            user.emp_id = self.env['hr.employee'].search(
                [('id', 'in', user.employee_ids.ids),
                 ('company_id', '=', self.env.company.id)], limit=1)

    @api.model
    def action_export_access(self):
        export_group = self.env.ref('base.group_allow_export')
        all_users = self.env['res.users'].search([('share', '=', False)])
        all_users.write({'groups_id': [(4, export_group.id)]})
