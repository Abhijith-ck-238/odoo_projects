from odoo import models, fields, api, _
from odoo.exceptions import UserError

class HelpdeskResources(models.Model):
    _name = "helpdedesk.resource"

    categ_id = fields.Many2one('helpdedesk.resource.category', string="Category", required=True)
    # categ_name = fields.Char('Category')
    # categ_type = fields.Selection([('human', 'Human'), ('vehicle', 'Vehicle')], "Category Type", default="human")
    categ_type = fields.Selection(string="Category Type", related='categ_id.type')
    qty = fields.Integer("Quantity", default=0, required=True)
    user_ids = fields.Many2many("res.users")
    vehicle_ids = fields.Many2many("fleet.vehicle")
    vehicle_mode_id = fields.Many2one("fleet.vehicle.model", string="Requestd Vehicle")
    note = fields.Char()
    remaining_qty = fields.Integer(compute="_check_remaining_qty")
    helpdesk_ticket_id = fields.Many2one('helpdesk.ticket', ondelete='cascade', readonly=True)

    @api.depends("qty")
    def _check_remaining_qty(self):
        for line in self:
            if line.categ_type == 'human':
                line.remaining_qty = line.qty - len(line.user_ids)
            elif line.categ_type == 'vehicle':
                line.remaining_qty = line.qty - len(line.vehicle_ids)
            else:
                line.remaining_qty = line.qty

    @api.onchange('categ_type')
    def _on_catge_id_change(self):
        for line in self:
            if line.categ_type == 'human':
                line.vehicle_ids = False
                line.vehicle_mode_id = False
            else:
                line.user_ids = False


class HelpdeskResourcesCategory(models.Model):
    _name = "helpdedesk.resource.category"

    name = fields.Char(string="Category Name", required=True)
    type = fields.Selection([('human', 'Human'), ('vehicle', 'Vehicle')], default='human', required=True)
