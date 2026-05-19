# -*- coding: utf-8 -*-
{
    'name': "Access Units",

    'summary': """Access Units""",

    'description': """
        A module for controlling user access for products, sale order and purchase orders
    """,

    'author': "Integrated Path",
    'website': "https://www.int-path.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/13.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Technical Settings',
    'version': '18.0.0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','sale_management','purchase','hr','product'],

    # always loaded
    'data': [
        'data/access_unit_rule.xml',
        'security/ir.model.access.csv',
        'views/views.xml',
        'views/access_units_views.xml',
        'views/sale_order_view.xml',
    ],
}
