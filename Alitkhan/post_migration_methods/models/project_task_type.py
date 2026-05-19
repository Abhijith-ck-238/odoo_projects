# -*- coding: utf-8 -*-
from odoo import api, fields, models


class ProjectTaskType(models.Model):
    """ This class is inherited to clean unwanted stages in field service"""
    _inherit = 'project.task.type'
    _description = 'ProjectTaskType'


    def clean_fs_stages(self):
        """Archive the unwanted field service stages"""
        stage_1 = self.env.ref('industry_fsm.planning_project_stage_1').id
        self.env.ref('industry_fsm.planning_project_stage_2').action_archive()
        self.env.ref('industry_fsm.planning_project_stage_3').action_archive()
        self.env.ref('industry_fsm.planning_project_stage_4').action_archive()
        self.env.cr.execute(f'''
            UPDATE project_task_type 
            SET name = '{{"en_US": "Done"}}',
                sequence = 7
            WHERE id = {stage_1}
        ''')

class Task(models.Model):
    """Inherits the data model to run action to add task_id"""
    _inherit = 'project.task'

    def assign_task_in_sale_line(self):

        for rec in self.filtered('sale_order_id'):
            lines = rec.sale_order_id.order_line.filtered(lambda l : not l.task_id)
            if lines:
                lines.task_id = rec.id