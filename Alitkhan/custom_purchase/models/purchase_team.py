from odoo import api, models, fields


class ResUsersExtend(models.Model):
    _inherit = 'res.users'

    purchase_team_id = fields.Many2one('purchase.team', 'Purchase Team')


class PurchaseTeam(models.Model):
    _name = 'purchase.team'

    name = fields.Char(string="Team")
    warehouse_id = fields.Many2one('stock.warehouse', string="Warehouse")
    member_ids = fields.One2many(
        'res.users', 'purchase_team_id', string='Members')
    company_id = fields.Many2one('res.company', string="Company")

    @api.model
    def _get_default_team_id(self, user_id=None, domain=None):
        if not user_id:
            user_id = self.env.uid
        team_id = self.env['purchase.team'].search([
            ('member_ids', 'in', user_id),
            '|', ('company_id', '=', False),
            ('company_id', '=', self.env.company.id)
        ], limit=1)
        if not team_id and 'default_team_id' in self.env.context:
            team_id = self.env['purchase.team'].browse(
                self.env.context.get('default_team_id'))
        if not team_id:
            team_domain = domain or []
            default_team_id = self.env['purchase.team'].search(team_domain,
                                                               limit=1)
            return default_team_id or self.env['purchase.team']
        return team_id
