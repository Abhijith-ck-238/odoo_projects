# -*- coding: utf-8 -*-
{
    'name': "Custom Pledges",

    'summary': """Customizations Pledges""",

    'description': """ 
                    1. Added archive option on pledges.
                    2. Amendments.
                   """,

    'author': "",
    'website': "",
    'category': 'Uncategorized',
    'version': '18.0.0.2',
    'sequence': 1,

    'pre_init_hook': 'pre_init_hook',


    # any module necessary for this one to work correctly
    'depends': ['pledge_assets'],

    # always loaded
    'data': [
        'data/mail_template.xml',
        'data/discuss_channel.xml',
        'data/action_deadline_notification.xml',
        'data/stage_change_activity.xml',
        'security/user_group.xml',
        'security/ir.model.access.csv',
        'views/pledges_form_view.xml',
        'views/lc_type.xml',
        'views/pledge_fom.xml',
        'views/pledge_view_kanban.xml',
        'views/pledge_stage.xml',
        'views/field_access.xml',
        'report/pledge_report_views.xml'

    ],
    'application': False,
    'installable': True,
    'auto_install': False,

}
