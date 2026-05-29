
# -*- coding: utf-8 -*-
{
    'name': "Import Purchase",

    'summary': """ Importing a Purchase Order """,

    'description': """ Importing a Purchase Order from excel sheet """,

    'author': "",
    'website': "",
    'category': 'purchase',
    'version': '18.0.0.1',
    'sequence': 1,

    # any module necessary for this one to work correctly
    'depends': ['import_purchase','access_units','stock'],

    # always loaded
    'data': [
        "security/ir.model.access.csv",
        'wizard/custom_import_purchase.xml',
        'views/purchase_view.xml',
        'views/product_view.xml',
    ],
    'application': True,
    'installable': True,
    'auto_install': False,
}

