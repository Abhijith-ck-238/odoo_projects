# -*- coding: utf-8 -*-
{
    'name': "Itkan Expenses Total IQD and USD Seperated",

    'summary': """
       This custom module is created for Al-Itkan to show expense lines total per currency """,

    'description': """
        This custom module is created for Al-Itkan to show expense lines total per currency
    """,

    'author': "Ahmed Naseem",
    'website': "http://www.int-path.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/13.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '18.0.0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','hr_expense'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/views.xml',
        'views/templates.xml',
        'views/hr_expense_sheet.xml',
        'reports/expense_report_report.xml'
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
