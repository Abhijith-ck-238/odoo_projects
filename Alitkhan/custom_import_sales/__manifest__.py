
# -*- coding: utf-8 -*-
{
    'name': "Import Sales",

    'summary': """ Importing a sale Order """,

    'description': """ Importing a Sale Order from excel sheet """,

    'author': "",
    'website': "",
    'category': 'sale',
    'version': '18.0.0.1',
    'sequence': 1,

    # any module necessary for this one to work correctly
    'depends': ['import_sale_order','custom_sales','access_units'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'data/product_pricelist_data.xml',
        'views/sale.xml',
    ],
    'application': True,
    'installable': True,
    'auto_install': False,
}

