from odoo import models, fields, api


class CustomIrAttachment(models.Model):
    _inherit = 'ir.attachment'

    new_name = fields.Char('Name', compute='compute_new_name')
    name_new = fields.Char('New Name')

    @api.depends('res_model', 'res_id')
    def compute_new_name(self):
        """ Method to compute new name for attachments"""
        for rec in self:
            if rec.res_model == 'project.task':
                if rec.res_id != 0:
                    task_id = self.env['project.task'].browse(rec.res_id)
                else:
                    self.env.cr.execute("""
                        SELECT pt.id
                        FROM project_task pt
                        JOIN attachement_task_service_report_rel rel ON rel.task_id = pt.id
                        WHERE rel.attachment_id = %s
                    """, (rec.id,))
                    result = self.env.cr.fetchone()
                    task_id = self.env['project.task'].browse(result[0]) if result else self.env['project.task']
                    # task_id = self.env['project.task'].search([]).filtered(
                    #          lambda l: rec.id in l.service_report_docs.ids)
                if task_id.service_report_id:
                    name = ""
                    if task_id.service_report_id.job_number:
                        name += "JN#" + task_id.service_report_id.job_number + " - "
                    if task_id.service_report_id.service_number:
                        name += "SN#" + task_id.service_report_id.service_number + " - "
                    if task_id.service_report_id.site:
                        name += task_id.service_report_id.site.site_name + " - "
                    if task_id.service_report_id.province:
                        name += task_id.service_report_id.province.name + " - "
                    if task_id.service_report_id.unit:
                        name += task_id.service_report_id.unit + " - "
                    if task_id.service_report_id.sn:
                        name += task_id.service_report_id.sn + " - "
                    if task_id.service_report_id.contract:
                        name += task_id.service_report_id.contract.name + " - "
                    if task_id.service_report_id.description:
                        name += task_id.service_report_id.description + " - "
                    if task_id.service_report_id.date:
                        name += str(task_id.service_report_id.date)
                    if name != "":
                        rec.new_name = name
                        rec.name_new = name
                    else:
                        rec.new_name = False
                        rec.name_new = False
                else:
                    rec.new_name = False
                    rec.name_new = False
            else:
                rec.new_name = False
                rec.name_new = False

    @api.model
    def set_id_and_resource_name(self):
        """ Scheduled action to set resource id and resource name in attachments for model project.task and
        if they are empty ."""
        attachment_ids = self.env['ir.attachment'].search(
            [('res_model', '=', 'project.task')])
        for rec in attachment_ids:
            if rec.res_id == 0:
                fs_id = self.env['project.task'].search(
                    [('service_report_docs', 'in', rec.id)])
                if fs_id:
                    rec.res_id = fs_id.id
                    rec.res_name = fs_id.name
                else:
                    rec.public = True
