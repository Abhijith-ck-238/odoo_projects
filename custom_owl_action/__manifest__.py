# -*- coding: utf-8 -*-
{
    'name': 'Custom OWL Action',
    'version': '18.0.1.0.0',
    'summary': 'Demo of useExternalListener hook in Odoo 18',
    'description': 'A module to demonstrate the useExternalListener hook in Odoo 18 using OWL.',
    'category': 'Hidden',
    'author': 'Developer',
    'depends': ['base', 'web'],
    'data': [
        'views/custom_owl_action_views.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'custom_owl_action/static/src/js/custom_component.js',
            'custom_owl_action/static/src/xml/custom_component.xml',
        ],
    },
    'installable': True,
    'application': True,
    'license': 'LGPL-3',
}
