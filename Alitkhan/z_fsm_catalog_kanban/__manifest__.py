# -*- coding: utf-8 -*-
{
    'name': "FSM Catalog Kanban",

    'summary': """FSM Catalog Kanban """,

    'description': """ """,

    'author': "",
    'website': "",
    'category': 'Operations/Field Service',
    'version': '18.0.0.1',
    'sequence': 1,

    # any module necessary for this one to work correctly
    'depends': ['custom_industry_fsm' ,'industry_fsm', 'industry_fsm_sale', 'industry_fsm_stock','sale_stock','account'],

    # always loaded
    'data': [
    ],
    'assets': {
        'web.assets_backend': [
             'z_fsm_catalog_kanban/static/src/product_catalog/kanban_record.js',
            'z_fsm_catalog_kanban/static/src/product_catalog/sale_order_line.js',
            'z_fsm_catalog_kanban/static/src/product_catalog/product_kanban_record.js',
            'z_fsm_catalog_kanban/static/src/components/account_payment_field/account_payment_field.js',
        ]
    },
    'application': False,
    'installable': True,
    'auto_install': False,

}
