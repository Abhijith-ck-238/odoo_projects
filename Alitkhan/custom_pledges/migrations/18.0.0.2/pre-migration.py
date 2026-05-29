from odoo import api, SUPERUSER_ID, Command


def migrate(cr, version):
    env = api.Environment(cr, SUPERUSER_ID, {})
    print("AAAAAAAAAAAAAAAAAAa")
    env['ir.model.data'].search([
        ('module', '=', 'custom_pledges'),
        ('name', '=', 'action_pledge_assets_kanban')
    ]).write({'noupdate': False})
    env.ref('custom_pledges.action_pledge_assets_kanban').write({'view_ids':[(env.ref('custom_pledges.pledge_asset_view_kanban'), 'kanban'), (env.ref('custom_pledges.pledge_pledge_view_form'), 'form')]})
    env.cr.commit()
