# -*- coding: utf-8 -*-


from datetime import timedelta

from odoo import api, fields, models, tools, SUPERUSER_ID, _
from odoo.exceptions import UserError, AccessError, ValidationError
from odoo.tools.safe_eval import safe_eval
from odoo.tools.misc import format_date
import logging
_logger = logging.getLogger(__name__)


class project_template(models.Model):
    _name = 'project.template'


    name = fields.Char(required=True)
    project_template_stage_ids = fields.One2many('project.template.stage','project_template_id', ondelete='cascade', required=True)
    project_template_task_ids = fields.One2many('project.template.task','project_template_id', ondelete='cascade', required=True)
    state = fields.Selection([
            ('draft', 'Draft'),
            ('done', 'Done'),
            ],default='draft')


    def done_progressbar(self):
        for rec in self:
            if not rec.project_template_stage_ids:
                _logger.info("****ERRORERRORERROR1****")
                raise ValidationError("List of stages is empty")
            if not rec.project_template_task_ids:
                _logger.info("****ERRORERRORERROR2****")
                raise ValidationError("List of tasks is empty")
            rec.write({'state': 'done',}) 




class project_template_stage(models.Model):
    _name = 'project.template.stage'

    stage_id = fields.Many2one('project.task.type', required=True)
    project_template_id = fields.Many2one('project.template', ondelete='cascade')


class project_template_task(models.Model):
    _name = 'project.template.task'

    name = fields.Char()
    task_weight = fields.Integer()
    project_template_id = fields.Many2one('project.template', ondelete='cascade')
