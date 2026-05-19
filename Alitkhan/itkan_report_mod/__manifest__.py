# -*- coding: utf-8 -*-
{
    'name': "Al-Itkan Report Module",

    'summary': """A Module For Al-Itkan Reports Constumization""",

    'author': "Ahmed Naseem, Mohammed Saeb @Integerated Path",
    'website': "https://www.int-path.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/13.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'itkan_bank_ext','account'],

    # always loaded
    'data': [
        'views/views.xml',
        'views/templates.xml',
        'views/invoice_report_mod.xml'
    ],
}
