# -*- coding: utf-8 -*-
{
    'name': "Equipments",

    'summary': """ """,

    'description': """

                   """,

    'author': "",
    'website': "",
    'category': 'Uncategorized',
    'version': '18.0.1.0.0',
    'sequence': 1,

    # any module necessary for this one to work correctly
    'depends': ['base', 'mail','hr','access_units', 'web'],

    # always loaded
    'data': [
        'security/user_group.xml',
        'security/ir.model.access.csv',
        'views/equipment_view.xml',
        'views/equipment_type_view.xml',
        'views/equipment_status_view.xml',
        'views/equipment_condition.xml',
        'views/hr_employee_view.xml',
        # 'views/filter_menu.xml',
        'views/equipment_tools_view.xml'
    ],
    'assets': {
        'web.assets_backend': [
            # 'custom_equipment/static/src/js/filter_menu.js',
            # 'custom_equipment/static/src/xml/filter_menu.xml',


        ],
    },

    'application': True,
    'installable': True,
    'auto_install': False,
}