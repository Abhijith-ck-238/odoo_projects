# -*- coding: utf-8 -*-
{
    'name': "Offering Import",

    'summary': """Offering import """,

    'description': """ Importing of Offering from excel sheet """,

    'author': "",
    'website': "",
    'category': 'Sales',
    'version': '18.0.0.1',
    'sequence': 1,

    # any module necessary for this one to work correctly
    'depends': ['base', 'itkan_offering', 'product','itkan_custom_sales_order'],

    # always loaded
    'data': [
         'security/ir.model.access.csv',
        'views/action_set_compressed_product_name.xml',
        'views/product_view.xml',
        'views/offering_offering.xml',
        'wizard/offer_warning_wizard.xml',

        'wizard/offering_import_view.xml',
        'views/internal_reference.xml',
        'views/offering_config_view.xml',
        'views/offering_search_view.xml',
        'views/config_search_view.xml',
    ],
    'application': True,
    'installable': True,
    'auto_install': False,

}
