# -*- coding: utf-8 -*-
{
    'name': "Custom Employee",

    'summary': """ Custom Employee""",

    'description': """ Adding sub items to operations tab with section 
    label as main product name """,

    'author': "",
    'website': "https://www.int-path.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/13.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'hr',
    'version': '18.0.1.0.0',
    'sequence': 1,

    # any module necessary for this one to work correctly
    'depends': ['base', 'hr', 'al-itkan', 'itkan_approvals_employee_info','itkan_searchpanel'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/divisions_view.xml',
        'views/unit_view.xml',
        'views/set_divisions_and_unit.xml',
        'views/hr_employee_views.xml',
        'views/res_users_view.xml',
    ],
    'application': True,
    'installable': True,
    'auto_install': False,

}
