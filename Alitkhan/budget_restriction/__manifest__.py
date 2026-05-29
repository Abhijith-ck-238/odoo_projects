# -*- coding: utf-8 -*-
{
    'name': 'Budget Restriction',
    "version": "18.0.1.0.1",
    'summary': 'Budget Restriction',
    'description': '''
        Budget Restriction
    ''',
    'category': 'Uncategorized',
    'author': 'Cybrosys Techno Solutions',
    'company': 'Cybrosys Techno Solutions',
    'maintainer': 'Cybrosys Techno Solutions',
    'website': 'https://www.cybrosys.com',
    'depends': [
    'base',
    'hr',
    'hr_expense',
    'custom_expense',
    'project',
    'analytic',
    'product',
    'accountant',
    'account_budget',
    'hr_expense_advance_clear'
    ],
    'data': [
        'security/ir.model.access.csv',
        'security/budget_policy_security.xml',
        'data/ir_cron.xml',
        'views/hr_expense_budget_policy_views.xml',
        'views/hr_expense_budget_consumption_views.xml',
        'views/budget_policy_tag_views.xml',
        'views/hr_expense_sheet_views.xml',
        'views/hr_employee_views.xml',
        'views/hr_expense_views.xml',
        'views/ir_budget_consumption_recompute.xml',
        'data/mail_template.xml'
    ],
    'assets': {
        'web.assets_backend': [
            'budget_restriction/static/src/js/analytic_distribution.js',
            'budget_restriction/static/src/xml/analytic_distribution.xml',
        ],
    },
    'license': 'LGPL-3',
    'installable': True,
    'application': False,
    'auto_install': False,
}
