from odoo import models, api


class CustomSaleOrder(models.Model):
    _inherit = 'sale.order'

    @api.model
    def create(self, vals):
        team_id = self.env['crm.team']._get_default_team_id()
        vals['warehouse_id'] = team_id.default_warehouse_id.id
        return super(CustomSaleOrder, self).create(vals)

    @api.onchange('company_id')
    def _onchange_company_id(self):
        self.warehouse_id = self.team_id.default_warehouse_id

    @api.onchange('team_id')
    def _onchange_team_id(self):
        self.warehouse_id = self.team_id.default_warehouse_id
