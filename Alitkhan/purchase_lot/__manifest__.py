# -*- coding: utf-8 -*-
{
    'name': "Purchase Lot/Serial Number",

    'summary': """
                    Purchase Lot and Serial Number

                    """,

    'description': """ This module helps to control Lot and Serial Number for Products from Purchase Application """,

    'author': "ALITKAN ",
    'website': "https://alitkan.com/",
    'category': 'purchase',
    'version': '18.0.1.0.0',
    'sequence': 100,

    # any module necessary for this one to work correctly
    'depends': ['base', 'stock', 'purchase'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/purchase_order_views.xml',
        'views/purchase_product_lot_views.xml'
    ],
    'application': True,
    'installable': True,
    'auto_install': False,
}

