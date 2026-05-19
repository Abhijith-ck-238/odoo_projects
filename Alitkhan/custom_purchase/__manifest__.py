# -*- coding: utf-8 -*-
{
    'name': "Custom Purchase",
    'summary': """ Customizations on Purchase module. """,
    'description': """
                        1. Add purchase team.
                   """,
    'author': "",
    'website': "",
    'category': 'Uncategorized',
    'version': '18.0.0.0',
    'sequence': 1,
    # any module necessary for this one to work correctly
    'depends': ['base', 'contacts', 'purchase', 'purchase_stock', 'itkan_offering', 'logistics'],
    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'reports/offering_purchase_order_header.xml',
        'reports/report_purchaseorder_document.xml',
        'reports/report_purchasequotation_document.xml',
        'views/res_users.xml',
        'views/purchase_team_views.xml',
        'views/purchase_views.xml',
        'views/account_move.xml',
        'wizard/shipment_create_wizard.xml',
    ],
    'application': False,
    'installable': True,
    'auto_install': False,
}
