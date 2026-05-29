# -*- coding: utf-8 -*-
{
    'name': "RFID Connector",

    'summary': """
                    
                    """,

    'description': """ """,

    'author': "",
    'website': "",
    'category': 'sales',
    'version': '18.0.0.1',
    'sequence': 1,

    # any module necessary for this one to work correctly
    'depends': ['product', 'stock'],

    # always loaded
    'data': [
        'data/epc_sequence.xml',
        'security/ir.model.access.csv',
        'views/product_product.xml',
        'views/res_config_settings.xml',
        'views/rfid_tags_view.xml',
        'views/stock_production_lot.xml',
        'views/stock_picking.xml',
        'views/rfid_transfer_view.xml',
        'wizard/scan_confirm_wizard.xml',
    ],
    'assets':{
        'web.assets_backend': [
            'rfid_connector/static/src/js/qz-tray.js'
        ]
    },
    'application': True,
    'installable': True,
    'auto_install': False,
}
