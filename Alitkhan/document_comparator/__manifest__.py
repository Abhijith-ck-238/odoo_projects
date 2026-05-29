# -*- coding: utf-8 -*-
{
    'name': "Documents Comparator",

    'summary': "This Module is used to compare between a current list of items and P.O`s and S.O`s",


    'author': "Ahmed Naseem, Mohammed Saeb ",
    'website': "https://www.int-path.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/13.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Documents',
    'version': '18.0.1.0.0',

    # any module necessary for this one to work correctly
    'depends': ['base','sale_management', 'purchase','sale_purchase'],

    # always loaded
    'data': [
        'security/res_groups.xml',
        'security/ir.model.access.csv',
        # 'views/views.xml',
        'views/document_comparator_view.xml',
        'views/purchase_order_view.xml',
        'views/sale_order_view.xml',
    ],
}
