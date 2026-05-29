# -*- coding: utf-8 -*-
{
    'name': "Custom CRM",

    'summary': """ Custom CRM""",

    'description': """ """,

    'author': "",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/13.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Sales/CRM',
    'version': '18.0.0.1',
    'sequence': 1,

    # any module necessary for this one to work correctly
    'depends': ['base', 'crm'],

    # always loaded
    'data': [
        'security/user_group.xml',
        'security/ir.model.access.csv',
        'views/crm_team.xml',
    ],
    'application': True,
    'installable': True,
    'auto_install': False,

}