# -*- coding: utf-8 -*-
{
    'name': "Al-Itkan Custom Sales Order",

    'summary': """
        Custom Sale Order For Al-Itkan""",

    'author': "INTEGRATED PATH",
    'website': "https://www.int-path.com/",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/13.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '18.0.0.1.0',

    # any module necessary for this one to work correctly
    'depends': ['base', 'sale', 'stock' , 'account','sale_management','itkan_offering'],

    # always loaded
    'data': [
        'security/security.xml',
        'views/views.xml',
        'report/report.xml',
        'report/report_temp.xml',
        'report/report_header.xml',
        'report/report_custom_external_layout.xml',
        'report/report_footer.xml'
    ],
}
