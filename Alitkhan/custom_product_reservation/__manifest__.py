# -*- coding: utf-8 -*-
{
    'name': "Product Reservation",

    'summary': """ """,

    'description': """

                   """,

    'author': "",
    'website': "",
    'category': 'Uncategorized',
    'version': '18.0.1.0.0',
    'sequence': 1,

    # any module necessary for this one to work correctly
    'depends': ['base', 'product', 'stock', 'hr', 'contracts'],

    # always loaded
    'data': [
        'data/product_reservation_activity.xml',
        'data/product_reservation_sequence.xml',
        'security/user_group.xml',
        'security/ir.model.access.csv',
        'views/product_reservation.xml'
    ],
    'application': True,
    'installable': True,
    'auto_install': False,

}