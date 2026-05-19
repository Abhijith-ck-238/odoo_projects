# -*- coding: utf-8 -*-
{
    'name': "Sale Lot",

    'summary': """
                    Sale Lot 

                    """,

    'description': """ This module helps to control Lot for Products from Sales Application """,

    'author': "ALITKAN ",
    'website': "https://alitkan.com/",
    'category': 'sales',
    'version': '18.0.1.0.0',
    'sequence': 100,

    # any module necessary for this one to work correctly
    'depends': ['base', 'mai_sale_order_lot_selection', 'qr_control',],

    # always loaded
    'data': [
        'data/ir_cron.xml',
        'views/stock_production_lot_views.xml',
        'views/sale_order_views.xml',
        'views/res_config_settings_views.xml',
        'views/production_lot_views.xml'
    ],
    'application': True,
    'installable': True,
    'auto_install': False,
    'post_init_hook': "set_stock_product_unreserved_qty",
}
