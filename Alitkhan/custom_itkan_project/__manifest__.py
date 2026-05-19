# -*- coding: utf-8 -*-
{
    'name': "ALITKAN Project",

    'summary': """ """,

    'description': """
                    
                   """,

    'author': "",
    'website': "",
    'category': 'Uncategorized',
    'version': '18.0.1.0.0',
    'sequence': 1,

    # any module necessary for this one to work correctly
    'depends': ['base','mail','custom_contract'],

    # always loaded
    'data': [
        'data/deadline_reminder_activity.xml',
        'data/sned_notification_cron.xml',
        'security/user_group.xml',
        'security/ir.model.access.csv',
        'views/project_views.xml',
        'views/ticket_stage.xml',
        'views/project_type.xml',
        'views/project_department.xml',
        'views/project_type.xml',
        'views/project_subtask.xml',
        'views/res_config_settings.xml',
        'views/contract_contract.xml',
        'report/itkan_project_report_views.xml'
    ],
    'application': True,
    'installable': True,
    'auto_install': False,

}
