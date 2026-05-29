# -*- coding: utf-8 -*-
{
    'name': "Custom Stock",

    'summary': """                  
      """,

    'description': """ Transfer customizations:
                       1.Delivery - Adding new field for related contract.
                       2. Added menu for showing duplicated inventory valuation entries.
  """,

    'author': "",
    'website': "",
    'category': 'sales',
    'version': '18.0.0.1',
    'sequence': 1,

    # any module necessary for this one to work correctly
    'depends': ['deltatech_product_do_merge', 'stock_account', 'sale_stock','itkan_custom_sales_order','stock'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        # 'views/assets.xml',
        'views/stock_picking_view.xml',
        'views/product_view.xml',
        'views/stock_valuation.xml',
        'wizard/merge_product_view_wizard.xml',
        'views/menu.xml',
        'wizard/merge_product_view_wizard.xml',
        'wizard/stock_picking_return_views.xml',


    ],
    'assets': {
        'web.assets_backend': [
            'custom_stock/static/src/js/remove_duplicate.js',
            'custom_stock/static/src/xml/stock_valuation_report.xml',
        ],
    },

    'qweb': ['static/src/xml/stock_valuation_report.xml'],
    'application': False,
    'installable': True,
    'auto_install': False,
}
