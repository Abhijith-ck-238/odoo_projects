from odoo import models, fields, api, _


class ProjectSubTasks(models.Model):
    _name = 'project.subtask'
    _description = 'Project Subtask'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char("Subtask Name")
    user_ids = fields.Many2many("res.users", string="Assignees")
    state = fields.Selection(selection=[("draft", "Draft"),("done", "Done")], default="draft")
    checklist_line_id = fields.Many2one("project.checklist.line")
    is_checked = fields.Boolean(string="Is Checked", default=False)
    project_id = fields.Many2one('itkan.project',  string="Project", related="checklist_line_id.project_id", store=True)

    @api.model
    def create(self, vals):
        res = super(ProjectSubTasks,self).create(vals)
        if vals.get('user_ids'):
            for user in vals.get('user_ids'):
                self.env['mail.activity'].sudo().create({
                    'display_name': 'Subtask Assigned',
                    'summary': 'Subtask Assigned',
                        'note': _(
                            "You have assigned to the subtask %s."
                            ) % (res.name),
                        'date_deadline': fields.datetime.now(),
                        'user_id': user[1],
                        'res_id': res.id,
                        'res_model_id': self.env[
                            'ir.model'].search(
                            [('model', '=', 'project.subtask')],
                            limit=1).id,
                        'activity_type_id': self.env.ref(
                            'custom_itkan_project.mail_activity_checklist_subtask_assigned').id,
                    })
        return res

    def write(self, vals):
        res = super(ProjectSubTasks,self).write(vals)
        if vals.get('user_ids'):
            for user in vals.get('user_ids'):
                if user[0] == 4:
                    self.env['mail.activity'].sudo().create({
                        'display_name': 'Subtask Assigned',
                        'summary': 'Subtask Assigned',
                            'note': _(
                                "You have assigned to the subtask %s."
                                ) % (self.name),
                            'date_deadline': fields.datetime.now(),
                            'user_id': user[1],
                            'res_id': self.id,
                            'res_model_id': self.env[
                                'ir.model'].search(
                                [('model', '=', 'project.subtask')],
                                limit=1).id,
                            'activity_type_id': self.env.ref(
                                'custom_itkan_project.mail_activity_checklist_subtask_assigned').id,
                        })
        if vals.get('is_checked'):
            if vals.get('is_checked'):
                self.state = 'done'
            else:
                self.state = 'draft'
        return res

