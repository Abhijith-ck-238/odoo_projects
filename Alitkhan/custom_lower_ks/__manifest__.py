# -*- coding: utf-8 -*-
{
    'name': "Lower KS",

    'summary': """ """,

    'description': """
                    
                   """,

    'author': "",
    'website': "",
    'category': 'Uncategorized',
    'version': '18.0.1.0.0',
    'sequence': 1,

    # any module necessary for this one to work correctly
    'depends': ['base','mail','product'],

    # always loaded
    'data': [
        'data/lower_ks_task_reminder.xml',
        'data/ir_cron_data.xml',
        'security/user_group.xml',
        'security/ir.model.access.csv',
        'views/ticket_stage.xml',
        'views/ticket.xml',
        'views/ticket_type.xml',
        'views/work_sector.xml',
        'views/account.xml',
        'views/source.xml',
        'views/province.xml',
        'views/speciality.xml'
    ],
    'application': True,
    'installable': True,
    'auto_install': False,

}
