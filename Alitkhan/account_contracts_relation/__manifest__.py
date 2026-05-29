# -*- coding: utf-8 -*-
{
    'name': "Link Invoice to Contract",

    'summary': """
        This App is used to add a Many2one field in invoice to link invoice to contract, it is also used to add a
         smart button in contracts to redirect to each contract related invoice""",

    'description': """
        This App is used to add a Many2one field in invoice to link invoice to contract, it is also used to add a
         smart button in contracts to redirect to each contract related invoice
    """,

    'author': "Ahmed Naseem",
    'website': "http://www.int-path.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/13.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Accounting',
    'version': '18.0.0.0',

    # any module necessary for this one to work correctly
    'depends': ['base','account','contracts','hr_expense'],

    # always loaded
    'data': [
        
        'views/invoice_view_inh.xml',
        'views/contract_view_inh.xml',
        'views/hr_expense_sheet.xml'
       
    ],
}
