# -*- coding: utf-8 -*-
{
    'name': "Payment Letters",

    'summary': """ """,

    'description': """
                    
                   """,

    'author': "",
    'website': "",
    'category': 'Uncategorized',
    'version': '18.0.1.0.0',
    'sequence': 1,

    # any module necessary for this one to work correctly
    'depends': ['base','mail','product','contracts'],

    # always loaded
    'data': [
        'data/letter_ticket_activity.xml',
        'security/user_group.xml',
        'security/ir.model.access.csv',
        'views/ticket.xml',
        'views/ticket_type.xml',
        'views/ticket_stage.xml',
        'reports/letter_report.xml'
    ],
    'application': True,
    'installable': True,
    'auto_install': False,

}
