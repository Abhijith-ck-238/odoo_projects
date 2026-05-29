# -*- coding: utf-8 -*-
{
    'name': "TAC KS",

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
        'data/tac_ks_task_reminder.xml',
        'security/user_group.xml',
        'security/ir.model.access.csv',
        'views/ticket_stage.xml',
        'views/ticket.xml',
        'views/serial_number.xml',
        'views/ticket_type.xml',
        'views/product_checklist.xml',
        'views/product_checklist_item.xml',
        'reports/product_checklist_report_template.xml',
        'reports/product_checklist_report.xml',
    ],
    'application': True,
    'installable': True,
    'auto_install': False,

}
