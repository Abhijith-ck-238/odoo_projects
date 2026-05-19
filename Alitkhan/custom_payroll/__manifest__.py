# -*- coding: utf-8 -*-

{
    "name": "Custom Payroll",
    "version": "18.0.0.0",
    "category": "Human Resources",
    "sequence": 38,
    "summary": "Generate employee payslips automatically",
    "author": "",
    "depends": ['base', 'hr_payroll'],
    "data": [
        'security/ir.model.access.csv',
        "views/custom_hr_payroll.xml",
    ],
    "application": True,
    'installable': True,
    'auto_install': False,
}
