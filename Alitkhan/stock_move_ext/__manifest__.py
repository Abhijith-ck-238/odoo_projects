# -*- coding: utf-8 -*-
{
    'name': "Stock Moves Tree View Extension",

    'summary': """
        This module is created for Al-Itkan, it is used to add Source Document, customer, expiration, on-hand and forcasted quantity
        in the stock moves tree view
        - Updated : Added Vendor and Product type in product.product to use by DX in product moves report and offering - 07-07-2021 - Ahmed Naseem """,

    'description': """
         This module is created for Al-Itkan, it is used to add Source Document, customer, expiration, on-hand and forcasted quantity
        in the stock moves tree view
    """,

    'author': "Ahmed Naseem",
    'website': "http://www.int-path.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/13.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Stock',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','stock'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/views.xml',
        'views/templates.xml',
        'views/stock_move_inh.xml',
        'views/product_product_view.xml',
        
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
