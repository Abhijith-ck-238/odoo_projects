# -*- coding: utf-8 -*-
{
    'name': "Custom Products",

    'summary': """ """,

    'description': """
                        1. Remove fields from export for particular user group.
                   """,

    'author': "",
    'website': "",
    'category': 'Uncategorized',
    'version': '18.0.0.1',
    'sequence': 1,

    # any module necessary for this one to work correctly
    'depends': ['stock','product'],
    # always loaded
    'data': [
		'views/product_template.xml',
    ],
    'application': False,
    'installable': True,
    'auto_install': False,

}
