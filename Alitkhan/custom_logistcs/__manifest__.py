
# -*- coding: utf-8 -*-
{
    'name': "Custom Logistics and Shipment",

    'summary': """Logistics and Shipment - Filters and group by """,

    'description': """ Adding filtering and group by to logistics and shipment module. """,

    'author': "",
    'website': "https://www.int-path.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/13.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'logistics',
    'version': '18.0.0.0',
    'sequence': 1,

    # any module necessary for this one to work correctly
    'depends': ['logistics','custom_purchase'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/logistics_search_view.xml',
        'views/logistics_shipment.xml',
        'views/shipment_type.xml',
        'views/account_move.xml',
        'reports/logistics_report.xml'

    ],
    'application': True,
    'installable': True,
    'auto_install': False,

}

