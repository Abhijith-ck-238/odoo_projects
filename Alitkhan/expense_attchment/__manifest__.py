# -*- coding: utf-8 -*-
{
    'name': 'Expense attachment',
    'category': 'Accounting/Expenses',
    'version': '18.0.0.1',
    'sequence': 10,
    'summary': 'Attachment visibility in Expenses',
    'description': """
            This module is used to add Attachment visibility in Expenses 
    """,
    'depends': ['base','hr_expense'],
    'data': [
        'views/attachment_view.xml',
		'views/filter_views.xml',
],
    'installable': True,
    'application': False,
    'auto_install': False,
}