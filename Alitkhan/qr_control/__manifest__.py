# -*- coding: utf-8 -*-
{
    'name': "Q&R Control",

    'summary': """
                    Quality and Reservation Control
                    
                    """,

    'description': """ Quality and Reservation Control """,

    'author': "ALITKAN",
    'website': "https://alitkan.com/",
    'category': 'sales',
    'version': '18.0.1.0.0',
    'sequence': 1,
    # any module necessary for this one to work correctly
    'depends': ['base', 'stock', 'sale', 'sale_stock' ],

    'data': [
        'security/qr_security.xml',
        'security/ir.model.access.csv',
        'data/qr_import_data.xml',
        # 'views/list_decoration.xml',
        'views/qr_import_views.xml',
        'views/qr_reservation_views.xml',
        'views/product_views.xml',
        'views/stock_picking_views.xml',
        'views/stock_production_lot_view.xml',
        'report/reservation_report_views.xml',
        'wizard/qr_import_wizard_views.xml',
        'views/menuitems.xml',
    ],
    'assets': {
        # 'web.assets_backend': [
        #     "qr_control/static/src/css/decoration.css",
        # ],
    },
    'application': True,
    'installable': True,
    'auto_install': False,
}
