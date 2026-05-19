from . import models
from . import report


def pre_init_hook(env):
    print("preinithook")
    env['ir.model.data'].search([
        ('module', '=', 'custom_pledges'),
        ('name', '=', 'action_pledge_assets_kanban')
    ]).write({'noupdate': False})
    # env['ir.actions.act_window.view']
    env.ref('custom_pledges.action_pledge_assets_kanban').write({'view_ids': [
        (env.ref('custom_pledges.pledge_asset_view_kanban'), 'kanban'),
        (env.ref('custom_pledges.pledge_pledge_view_form'), 'form')]})
    env.ref('custom_pledges.action_pledge_assets_kanban')._compute_views()



