from odoo import models,fields


class HelpdeskResources(models.Model):
    _inherit = "helpdedesk.resource"

    categ_id = fields.Many2one('helpdedesk.resource.category', string="Category", required=True, ondelete="cascade")
