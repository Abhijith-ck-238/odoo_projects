# -*- coding: utf-8 -*-
{
    'name': "DX Sale Order",

    'summary': """
        This Report Was create for Al-itkan DX """,

    'description': """
        This Report Was create for Al-itkan DX
    """,

    'author': "Ahmed Naseem",
    'website': "http://www.int-path.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/13.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/views.xml',
        'views/templates.xml',
        'reports/dx_invoice_external_layout.xml',
        'reports/dx_invoice_footer.xml',
        'reports/dx_invoice_header.xml',
        'reports/dx_invoice.xml'

    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
