# -*- coding: utf-8 -*-
{
    'name': "Post migration methods",

    'summary': """
    Postmigration methods
      """,

    'description': """
        1. scheduled actions and scripts for data consistancy
    """,

    'author': " Cybrosys Technologies",
    'website': "",
    'category': 'Uncategorized',
    'version': '18.0.1.0.0',
    'application': False,
    'post_init_hook': 'post_init_hook',

    # any module necessary for this one to work correctly
    'depends': ['helpdesk', 'custom_lower_ks','web_gantt','web','industry_fsm','stock'],

    # always loaded
    'data': [
        'data/ir_cron.xml',
        'data/ir_actions_server_data.xml',
],
    'assets': {
        'web.assets_backend_lazy': [
            'post_migration_methods/static/src/**/*',
        ]
    },
}
