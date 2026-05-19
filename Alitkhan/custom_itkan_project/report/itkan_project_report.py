# -*- coding: utf-8 -*-

from odoo import tools
from odoo import api, fields, models


class ItkanProjectReport(models.Model):
    _name = "itkan.project.report"
    _description = "Itkan Project Analysis Report"
    _auto = False

    project_id = fields.Many2one('itkan.project', 'Project', readonly=True)
    progress = fields.Integer("Progress", readonly=True)
    done_checklist = fields.Integer("Done Steps", readonly=True)
    pending_tasks = fields.Integer("Pending Steps", readonly=True)
    late_steps = fields.Integer('Late Steps', readonly=True)
    department_id = fields.Many2one('project.department', readonly=True, string="Department")
    project_type_id = fields.Many2one('project.type', readonly=True, string="Project Type")
    checklist_name = fields.Char(string="Checklist")

    def init(self):
        tools.drop_view_if_exists(self.env.cr, "itkan_project_report")
        self.env.cr.execute("""CREATE or REPLACE VIEW itkan_project_report as (
        SELECT
            min(rl.id) as id,
            rl.id as project_id,
            rl.progress as progress,
            r.department_id as department_id,
            rl.project_type_id as project_type_id,
            r.checklist_name as checklist_name,
            sum(CASE WHEN r.is_checked = True THEN 1 ELSE 0 END) as done_checklist,
            sum(CASE WHEN r.is_checked = False and r.deadline >= CURRENT_DATE THEN 1 ELSE 0 END) as pending_tasks,
            sum(CASE WHEN r.is_checked = False and r.deadline < CURRENT_DATE THEN 1 ELSE 0 END) as late_steps
        FROM
               itkan_project rl
        JOIN
               project_checklist_line r on (rl.id=r.project_id)
        GROUP BY
            rl.id,
            rl.progress,
            r.department_id,
            r.checklist_name    
        )""")
