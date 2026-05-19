# -*- coding: utf-8 -*-
{
    'name': "Analytic Account",

    'summary': """Analytic Account - Account Group """,

    'description': """Set the analytic account and anaylitc account grop for users and show them in sales.""",

    'author': "",
    'website': "",
    'category': 'Accounting',
    'version': '18.0.1.0.0',
    'sequence': 1,

    # any module necessary for this one to work correctly
    'depends': ['base', 'analytic', 'account', 'custom_hr_expense_advance_clearng', 'sale'],

    # always loaded
    'data': [
        'security/groups.xml',
        'security/ir.model.access.csv',
        'views/account_analytic_line.xml',
        'views/account_analytic_plan.xml',
        'views/sale_anlalytic.xml'
    ],
    'application': True,
    'installable': True,
    'auto_install': False,

}
