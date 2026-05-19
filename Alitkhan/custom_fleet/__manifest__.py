# -*- coding: utf-8 -*-
{
    'name': "Custom Fleet",

    'summary': """ """,

    'description': """""",

    'author': "",
    'website': "",
    'category': 'Fleet',
    'version': '18.0.1.0.0',
    'sequence': 1,

    # any module necessary for this one to work correctly
    'depends': ['base', 'fleet','project','custom_helpdesk','itkan_fleet_customization'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/field_service.xml',
        'views/fleet_vehicle.xml',
        'views/fleet_service_type.xml'
    ],
    'assets': {
        'web.assets_backend': [
            'custom_fleet/static/src/js/fleet_one2many.xml',
            'custom_fleet/static/src/js/fleet_one2many.js',
        ]
    },
    'application': True,
    'installable': True,
    'auto_install': False,

}
