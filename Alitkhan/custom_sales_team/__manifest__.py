# -*- coding: utf-8 -*-
{
    'name': "Custom Sales Team",

    'summary': """
                 Default warehouse in sales team.   
                    """,

    'description': """ Adding default warehouse for the sales team. """,

    'author': "",
    'website': "",
    'category': 'sales',
    'version': '18.0.0.1',
    'sequence': 1,

    # any module necessary for this one to work correctly
    'depends': ['custom_sales', 'stock'],

    # always loaded
    'data': [
        'data/product_category.xml',
        'views/action_duplicate_product.xml',
        'views/sales_team.xml',
        'views/product_template.xml',
    ],
    'qweb': ['static/src/xml/button.xml'],

    'application': False,
    'installable': True,
    'auto_install': False,
}
