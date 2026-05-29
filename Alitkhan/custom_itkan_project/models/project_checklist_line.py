from odoo import models, fields, _, api


class ProjectChecklistLine(models.Model):
    _name = "project.checklist.line"
    _description = "Project Checklist Line"
    _rec_name = "checklist_name"


    checklist_name = fields.Char("Checkist")
    is_checked = fields.Boolean("Is Checked", compute="compute_is_checked", store=True, readonly=False)
    note = fields.Text("Note")
    deadline = fields.Date("Dead Line")
    project_id = fields.Many2one('itkan.project')
    have_sub_checklist = fields.Boolean("Have sub checklist")
    checklist_id = fields.Many2one('project.checklist', store=True)
    department_id = fields.Many2one('project.department', related="checklist_id.department_id", store=True)
    members = fields.Many2many('res.users')
    subtask_ids = fields.One2many('project.subtask', "checklist_line_id", "Subtask")
    progress = fields.Integer("Progress", compute="compute_progress")
    notify_before_days = fields.Integer("Notify before days")
    attachment_ids = fields.Many2many('ir.attachment', string="Attachments")

    @api.model
    def create(self, vals):
        res = super(ProjectChecklistLine, self).create(vals)
        attachment_ids = res.mapped('attachment_ids')
        attachment_ids.write({
            'res_id': res.id,
        })
        return res

    def compute_progress(self):
        for rec in self:
            total_subtask = len(rec.subtask_ids)
            true_sub_task = len(rec.subtask_ids.filtered(lambda c: c.is_checked ))
            if true_sub_task:
                rec.sudo().write({'have_sub_checklist':True,
                                          'progress': (true_sub_task/total_subtask)*100})
            else:
                rec.sudo().write({'progress': 0})


    @api.depends('subtask_ids.state')
    def compute_is_checked(self):
        for rec in self:
            states = rec.subtask_ids.search([('checklist_line_id', '=', rec.id)]).mapped('state')
            if states:
                if all(i == 'done' for i in states):
                    rec.is_checked = True
                else:
                    rec.is_checked = False
            else:
                rec.is_checked = False

    def action_checklist_line_form(self):
        context = dict(self.env.context)
        context[
            "form_view_ref"] = "custom_itkan_project.view_project_checklist_line_form"
        return {
            "name": "Checklist",
            "type": "ir.actions.act_window",
            "res_model": "project.checklist.line",
            "views": [[False, "form"]],
            "res_id": self.id,
            "context": context,
            "target": 'new',
        }

    def write(self, vals):
        if self.project_id:
            if vals.get('checklist_name'):
                message = "Checklist:" + str(self.checklist_name) + " --> " + str(
                    vals.get('checklist_name'))
                self.project_id.message_post(body=message)
            if vals.get('is_checked') or vals.get('is_checked') == False:
                message = "Is Checked for " + str(self.checklist_name) + " : " + str(self.is_checked) + " --> " + str(
                    vals.get('is_checked'))
                self.project_id.message_post(body=message)
            if vals.get('note'):
                message = "Note:" + str(
                    self.note) + " --> " + str(
                    vals.get('note'))
                self.project_id.message_post(body=message)
            if vals.get('deadline'):
                message = "Deadline for " + str(self.checklist_name) + " : " + str(
                    self.deadline) + " --> " + str(
                    vals.get('deadline'))
                self.project_id.message_post(body=message)
            if vals.get('progress'):
                message = "Progress:" + str(
                    self.progress) + " --> " + str(
                    vals.get('progress'))
                self.project_id.message_post(body=message)

        return super(ProjectChecklistLine, self).write(vals)
