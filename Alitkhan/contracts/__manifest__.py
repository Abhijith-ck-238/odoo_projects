# -*- coding: utf-8 -*-
{
    'name': "Contracts",

    'summary': """Manageing All Your Costumer Related Contracts""",

    'author': "Integerated Path",
    'website': "https://www.int-path.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/13.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Documents',
    'version': '18.0.0.1',

    # any module necessary for this one to work correctly
    'depends': ['product'],

    'application': True,

    # always loaded
    'data': [
        'security/res_groups_data.xml',
        'security/ir.model.access.csv',
        'views/contract_views.xml',
        'views/contract_contract_views.xml',
        'views/contract_product_views.xml',
        'views/contract_province_views.xml',
        'views/contract_modality_views.xml',
        'views/contract_sites_views.xml'
    ],
}
