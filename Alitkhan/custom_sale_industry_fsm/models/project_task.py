from odoo import models, fields, api, _, SUPERUSER_ID
from odoo.exceptions import UserError


class CustomProjectTask(models.Model):
    _inherit = "project.task"
    
    #TODO: commented to fix the FSM stages order issue

    # @api.model
    # def _read_group_stage_ids(self, stages, domain,order = None):
    #     if 'fsm_mode' in self.env.context.keys():
    #         if self.env.context['fsm_mode']:
    #             project_id = self.env['project.task.type'].search(
    #                 [('project_ids', 'in',
    #                   self.env['project.project'].search(
    #                       [('name', 'ilike', 'Field Service')]).ids)])
    #             search_domain = [('id', 'in', project_id.ids)]
    #         else:
    #             search_domain = [('id', 'in', stages.ids)]
    #     else:
    #         search_domain = [('id', 'in', stages.ids)]
    #     if 'default_project_id' in self.env.context:
    #         search_domain = ['|', ('project_ids', '=', self.env.context[
    #             'default_project_id'])] + search_domain
    #
    #     stage_ids = stages._search(search_domain, order=order)
    #     return stages.browse(stage_ids)

    sale_order_char = fields.Char(string="Sale order",related='sale_order_id.name')
