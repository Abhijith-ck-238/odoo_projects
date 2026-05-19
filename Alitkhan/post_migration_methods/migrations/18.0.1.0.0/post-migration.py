from odoo import api, SUPERUSER_ID


def migrate_data(env):
    env.ref('industry_fsm.planning_project_stage_1').write({'name':'Done','sequence':7})
    env.ref('industry_fsm.planning_project_stage_2').action_archive()
    env.ref('industry_fsm.planning_project_stage_3').action_archive()
    env.ref('industry_fsm.planning_project_stage_4').action_archive()



# def migrate(cr, version):
#     env = api.Environment(cr, SUPERUSER_ID, {})
#     migrate_data(env)