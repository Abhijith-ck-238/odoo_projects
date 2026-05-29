# -*- coding: utf-8 -*-
{
    'name': "Offering",

    'summary': """Sale Offering""",

    'description': """From Offering to Quatations""",

    'author': "Ahmed Naseem, Mohammed Saeb @Integerated Path",
    'website': "https://www.int-path.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/13.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Sales',
    'version': '18.0.0.1.0',

    'application': True,

    # any module necessary for this one to work correctly
    'depends': ['base', 'product', 'sale_management',
                'contracts', 'contacts',
                'purchase', 'mrp', 'product_expiry',
                'product_bundle_pack', 'access_units', 'res_partner_extension'],

    # always loaded
    'data': [
        'security/groups.xml',
        'security/ir.model.access.csv',
        'views/views.xml',
        'views/res_company_view.xml',
        'views/offering_config_view.xml',
        'views/offering_offering_view.xml',
        'views/purchase_order_inh_view.xml',
        'views/sale_order_inh_view.xml',
        'views/contract_contract_view.xml',
        'views/offering_template_view.xml',
        'data/offering_access_unit_data.xml',
        'reports/offering_offering_report.xml',
        'reports/xlsx_report_actions.xml',
        'reports/offering_arabic_report.xml'
    ],
    'assets': {
        'web.assets_backend': [
            'itkan_offering/static/src/js/action_manager.js'
        ]
    },
}
