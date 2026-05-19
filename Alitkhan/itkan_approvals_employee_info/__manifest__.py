# -*- coding: utf-8 -*-
{
    'name': "Itkan approvals employee info",

    'summary': """
        Automatically getting employee info in approvals""",

    'author': "INTEGRATED PATH",
    'website': "https://int-path.com/",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/13.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '18.0.1.0.0',

    # any module necessary for this one to work correctly
    'depends': ['base', 'approvals'],

    # always loaded
    'data': [
        'views/approval_request_view.xml'
    ],
    'application': True,
    'installable': True,
    'auto_install': False,

}
