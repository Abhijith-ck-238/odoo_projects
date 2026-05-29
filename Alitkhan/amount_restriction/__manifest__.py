# -*- coding: utf-8 -*-
{
    'name': 'Amount Restriction',
    'version': '1.0',
    'summary': 'Brief description of the module',
    'description': '''
        Detailed description of the module
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
    'project',
    'analytic',
    'product',
    ],
    'data': [
        'security/ir.model.access.csv',
        'security/budget_policy_security.xml',
        'views/hr_expense_budget_policy_views.xml',
        'views/hr_expense_budget_consumption_views.xml',
        'views/budget_policy_tag_views.xml',
        'views/hr_expense_sheet_views.xml',
        'views/hr_employee_views.xml',
    ],
    'license': 'LGPL-3',
    'installable': True,
    'application': False,
    'auto_install': False,
}
