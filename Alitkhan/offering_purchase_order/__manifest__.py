# -*- coding: utf-8 -*-
{
    'name': "Itkan Offering Custom Purchase Order",

    'summary': """
        This custom module is created to implement itkan offering custom purchase order
       """,

    'description': """
        This custom module is created to implement itkan offering custom purchase order
    """,

    'author': "Ahmed Naseem",
    'website': "http://www.int-path.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/13.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Purchase',
    'version': '18.0.0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','purchase','contracts'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'reports/offering_purchase_order.xml',
        'reports/offering_po_external_layout.xml',
        'reports/offering_po_header.xml',
        'reports/offering_po_footer.xml',
        'views/purchase_order_inherit_view.xml',
        
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
