from odoo import models, fields

class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    policy_count = fields.Integer(
        string='Policy Count',
        compute='_compute_policy_count')

    def _compute_policy_count(self):
        for employee in self:
            employee.policy_count = self.env['hr.expense.budget.policy'].search_count([
                ('scope_employee_ids', 'in', employee.id)
            ])

    def action_view_employee_policies(self):
        """Open only the policies linked to this employee"""
        self.ensure_one()
        return {
            'name': 'Budget Policies',
            'type': 'ir.actions.act_window',
            'res_model': 'hr.expense.budget.policy',
            'view_mode': 'list,form',
            'domain': ['|', ('scope_employee_ids', '=', False), ('scope_employee_ids', 'in', self.id)]
        }
