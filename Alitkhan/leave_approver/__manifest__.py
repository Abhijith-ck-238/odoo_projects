# -*- coding: utf-8 -*-
{
    'name' : 'Leave Approval',
    'version' : '18.0.1.0',
    'summary': 'Leave',
    'sequence': 15,
    'description': """
    """,
    'category': 'Holiday',
    'depends' : ['hr_holidays','hr_recruitment'],
    'data': [
    	'security/ir.model.access.csv',
        'data/mail_template_data.xml',
        'views/employee_view.xml',
    ],
    'demo': [
    ],
    'qweb': [
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
