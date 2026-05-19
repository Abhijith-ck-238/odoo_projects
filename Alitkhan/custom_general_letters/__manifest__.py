# -*- coding: utf-8 -*-
{
    'name': "General Letters",

    'summary': """ General Letters""",

    'description': """
General Letters
                   """,

    'author': "",
    'website': "",
    'category': 'Uncategorized',
    'version': '18.0.1.0.0',
    'sequence': 1,
    'license': 'LGPL-3',

    # any module necessary for this one to work correctly
    'depends': ['base', 'mail', 'product'],


    'data': [
        'security/user_group.xml',
        'security/ir.model.access.csv',
        'data/letter_ticket_activity.xml',
        'views/ticket.xml',
        'views/ticket_type.xml',
        'views/ticket_stage.xml',
        'reports/letter_report.xml'
    ],

    'application': True,
    'installable': True,
    'auto_install': False,
}
