from odoo import models, fields


class CustomHelpDeskTicketType(models.Model):
    _inherit = "helpdesk.ticket.type"

    allowed_fs_stages = fields.Many2many('project.task.type',
                                         'helpdesk_ticket_type_rel',
                                         'helpdesk_ticket_type_id',
                                         'stage_id', domain=lambda self: [
        ('project_ids', 'in',
         self.env['project.project']
         .search([('name', 'ilike', 'Field Service')]).ids)
    ],
                                         string="Allowed FS Stages")

    is_to_hide_other_stages = fields.Boolean(string="Hide Other stages")
    is_reported_by_required = fields.Boolean(string="Reported by is required")
    show_contract_status = fields.Boolean(string="Show Contract Status")
    exception_id = fields.Many2one('helpdesk.ticket.exception',
                                   string="Exception Reason")
    subticket_exception_id = fields.Many2one('helpdesk.ticket.exception',
                                             string="Exception Reason for Sub ticket")
    bad_use = fields.Boolean(string="Bad Use")
    is_show_product_cart = fields.Boolean(string="Show Product Cart")
    can_edit_task_range = fields.Boolean(string="Edit Task Range")

