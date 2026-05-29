# -*- coding: utf-8 -*-


from datetime import timedelta

from odoo import api, fields, models, tools, SUPERUSER_ID, _
from odoo.exceptions import UserError, AccessError, ValidationError
from odoo.tools.safe_eval import safe_eval
from odoo.tools.misc import format_date
import logging
_logger = logging.getLogger(__name__)

class project_project(models.Model):
    _inherit = 'project.project'

    sum_weight = fields.Integer(compute='_fill_sum_weight')
    template_id = fields.Many2one('project.template',string="Template:")

    state = fields.Selection([
            ('new', 'New'),
            ('template', 'Template'),
            ('template_assigned', 'Template assigned'),
            ],default='new')

    def _fill_sum_weight(self):
        for rec in self:
            
            tasks = rec.env['project.task'].search([('project_id','=', rec.id)])
            if tasks:
                total_weight = 0
                for enreg in tasks:
                    if enreg.stage_id.state == 'done':
                        total_weight = total_weight + enreg.weight

                rec.sum_weight = total_weight
            else:
                rec.sum_weight = 0

    def template_progressbar(self):
        for rec in self:
            rec.write({'state': 'template',}) 


    def assign_template_progressbar(self):
        for rec in self:
            if rec.template_id:
                for enreg in rec.template_id.project_template_stage_ids:

                    enreg.stage_id.project_ids = [(4,rec.id)]
                for enreg in rec.template_id.project_template_task_ids:

                    enreg.env['project.task'].create(
                        {
                            'name': enreg.name,
                            'project_id': rec.id,
                            'weight': enreg.task_weight,
                        }
                    )
            else:
                x= 1
        rec.write({'state': 'template_assigned',}) 
