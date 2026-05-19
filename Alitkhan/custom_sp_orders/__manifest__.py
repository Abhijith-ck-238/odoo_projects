# -*- coding: utf-8 -*-
{
    'name': "Sp Orders",

    'summary': """ """,

    'description': """

                   """,

    'author': "",
    'website': "",
    'category': 'Uncategorized',
    'version': '18.0.0.1',
    'sequence': 1,

    # any module necessary for this one to work correctly
    'depends': ['base', 'product', 'stock', 'purchase', 'hr'],

    # always loaded
    'data': [
        'data/sp_orders_activity.xml',
        'data/sp_orders_sequence.xml',
        'security/user_group.xml',
        'security/ir.model.access.csv',
        'views/sp_orders.xml'
    ],
    'application': True,
    'installable': True,
    'auto_install': False,

}