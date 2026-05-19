from odoo import api, fields, models, _, Command
from datetime import timedelta
from odoo.exceptions import ValidationError
import requests


class ItkanProject(models.Model):
    _name = 'itkan.project'
    _description = "Itkan Project"
    _inherit = ['mail.thread', 'mail.activity.mixin']

    def _get_default_stage_id(self):
        return self.env['project.stage'].search([], order='sequence', limit=1)

    name = fields.Char('Project Name', tracking=True)
    stage_id = fields.Many2one('project.stage', string="Stage", copy=False,
                               default=_get_default_stage_id,
                               group_expand='_read_group_stage_ids',
                               tracking=True, store=True)
    project_manager = fields.Many2one('res.users', string=" Technical Project Manager", tracking=True)
    sales_project_manager = fields.Many2one('res.users',
                                      string="Sales Project Manager",
                                      tracking=True)
    contract_id = fields.Many2one('contract.contract', string="Contract", tracking=True)
    project_committee_users = fields.Many2many("res.users", string="Project Committee", tracking=True)
    starting_date = fields.Date("Starting Date", tracking=True)
    active = fields.Boolean("Active", default=True, tracking=True)
    color = fields.Integer("Color")
    project_type_id = fields.Many2one('project.type', string='Project Type', tracking=True)
    checklist_line_ids = fields.One2many('project.checklist.line', 'project_id', string="Checklist")
    progress = fields.Integer("Progress", compute="compute_progress", tracking=True, store=True)
    hide_checklist = fields.Boolean("Hide Checklist", default=False)
    show_checklist = fields.Boolean("Show Checklist", default=False)
    hide_checklist_default = fields.Boolean(compute="compute_hide_checklist_default")
    is_manager = fields.Boolean(compute="compute_is_manager")
    is_committee = fields.Boolean(compute="compute_is_manager")
    project_duration = fields.Integer("Project Duration(In Days)", tracking=True)
    ending_date = fields.Date("Ending Date", tracking=True)

    @api.onchange('project_duration', 'starting_date')
    def _onchange_project_duration(self):
        if self.project_duration and self.starting_date:
            self.ending_date = self.starting_date +timedelta(days=self.project_duration)

    def compute_is_manager(self):
        for rec in self:
            if rec.project_manager == self.env.user or rec.sales_project_manager == self.env.user:
                rec.is_manager = True
            else:
                rec.is_manager = False
            if rec.project_manager != self.env.user and rec.sales_project_manager != self.env.user and self.env.user in self.project_committee_users:
                rec.is_committee = True
            else:
                rec.is_committee = False


    def compute_hide_checklist_default(self):
        for rec in self:
            rec.hide_checklist = False
            rec.hide_checklist_default = False

    @api.onchange('contract_id')
    def onchange_contract_id(self):
        contract = self.env['contract.contract'].browse(self.contract_id.id)
        contract.itkan_project_id = self._origin

    @api.depends('checklist_line_ids.is_checked')
    def compute_progress(self):
        for rec in self:
            checklist = self.env['project.checklist.line'].search(
                [('project_id', '=', rec.id)])
            total_checklist = len(checklist)
            true_checklist = len(checklist.search(
                [('is_checked', '=', True), ('project_id', '=', rec.id)]))
            if total_checklist:
                rec.progress = (true_checklist / total_checklist) * 100
            else:
                rec.progress = 0

    @api.model
    def _read_group_stage_ids(self, stages, domain, order = None):
        return self.env['project.stage'].search([], order=order)

    @api.onchange('project_type_id')
    def onchange_project_type_id(self):
        if self.project_type_id and not self.starting_date:
            raise ValidationError(_("Please select the starting date!"))

        if self.project_type_id and self.starting_date:
            dic = {}
            vals = []
            key = False

            for line in self.project_type_id.checklist_ids:
                if not line.is_subtask:
                    if key:
                        dic[key] = vals
                    vals = []
                    key = line
                else:
                    vals.append(line)

            if key:
                dic[key] = vals

            commands = [Command.clear()]

            current_date = self.starting_date

            for main_task, subtasks in dic.items():
                members = main_task.department_id.team_members
                deadline = current_date + timedelta(days=main_task.days_for_project)
                commands.append(Command.create({
                    'checklist_id': main_task.id,
                    'checklist_name': main_task.name,
                    'deadline': deadline,
                    'members': members,
                    'notify_before_days': main_task.days_to_notify_before_deadline,
                    'subtask_ids': [Command.create({
                        'name': l.name,
                    }) for l in subtasks]
                }))

                current_date = deadline
            self.checklist_line_ids = commands

    def send_checklist_deadline_notification(self):
        projects = self.env['itkan.project'].search([])
        for project in projects:
            checklists = self.env['project.checklist.line'].search([('project_id', '=', project.id)])
            for checklist in checklists:
                if checklist.deadline:
                    notification_day = checklist.deadline - timedelta(days=checklist.notify_before_days)
                    if notification_day == fields.Date.today():
                        if not checklist.is_checked:
                            users = checklist.checklist_id.department_id.team_members
                            for user in users:
                                if user in project.project_committee_users or user == project.project_manager or user == project.sales_project_manager:
                                    self.env['mail.activity'].sudo().create({
                                        'display_name': 'Deadline Reached',
                                        'summary': 'Deadline Reached',
                                        'note': _("Dear %s,\n This email to remind you that this deadline will be met on for your information and "
                                                  "actions <a href=# data-oe-model=itkan.project data-oe-id=%d>%s</a> will end by %s days."
                                                  ) % (user.name, project.id, checklist.checklist_name, str(checklist.notify_before_days)),
                                        'date_deadline': fields.datetime.now(),
                                        'user_id': user.id,
                                        'res_id': project.id,
                                        'res_model_id': self.env[
                                            'ir.model'].search(
                                            [('model', '=', 'itkan.project')],
                                            limit=1).id,
                                        'activity_type_id': self.env.ref('custom_itkan_project.mail_activity_checklist_deadline_reached').id,
                                    })
                                    # notification_ids = [((0, 0, {
                                    #     'res_partner_id': user.partner_id.id,
                                    #     'notification_type': 'inbox'}))]
                                    message_body = _(
                                        "Dear %s,\n This email to remind you that this deadline will be met on for your information and "
                                        "actions <a href=# data-oe-model=itkan.project data-oe-id=%d>%s</a> will end by %s days."
                                    ) % (user.name, project.id, checklist.checklist_name,str(checklist.notify_before_days))
                                    project.message_post(
                                        body=message_body,
                                        message_type='comment',
                                        subtype_xmlid='mail.mt_comment',
                                        partner_ids=[user.partner_id.id],
                                        # notification_ids=notification_ids
                                    )
                                    number = user.partner_id.mobile
                                    template = self.env['whatsapp.template'].search(
                                        [('template_name', '=', 'test_itkan_connect_v4_copy')])
                                    account = template.wa_account_id
                                    if template:
                                        base_url = self.env["ir.config_parameter"].sudo().get_param("web.base.url")
                                        project_link = f"{base_url}/web#id={project.id}&model=itkan.project&view_type=form"

                                        body = template.body
                                        # body = body.replace("{{1}}", str(user.partner_id.name) or "")
                                        body = body.replace("{{1}}", str(checklist.checklist_name) or "")
                                        body = body.replace("{{2}}", str(project.name) or "")
                                        body = body.replace("{{3}}", str(checklist.notify_before_days) or "")
                                        body = body.replace("{{4}}", project_link)
                                        mail_message = self.env['mail.message'].create({
                                            'body': body,
                                            'model': 'itkan.project',
                                            'res_id': project.id,
                                            'message_type': 'comment',
                                        })

                                        self.env['whatsapp.message'].create({
                                            'wa_template_id': template.id,
                                            'mail_message_id': mail_message.id,
                                            'wa_account_id': account.id,
                                            'mobile_number': number,
                                            'body': body,
                                        })


                    if checklist.deadline == fields.Date.today():
                        if not checklist.is_checked:
                            project.stage_id = int(self.env['ir.config_parameter'].sudo().get_param('custom_itkan_project.stage_id'))
