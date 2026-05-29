# -*- coding: utf-8 -*-
{
    'name': "Custom Guest House",

    'summary': """ """,

    'description': """
                    
                   """,

    'author': "",
    'website': "",
    'category': 'Uncategorized',
    'version': '18.0.0.1',
    'sequence': 1,

    # any module necessary for this one to work correctly
    'depends': ['base', 'mail','al-itkan','custom_employees'],

    # always loaded
    'data': [
        'data/bed_sequence.xml',
        'data/reservation_activity.xml',
        'security/user_group.xml',
        'security/ir.model.access.csv',
        'views/guest_house_view.xml',
        'views/guest_house_bed_view.xml',
        'views/bed_reservation.xml',
        'wizard/reservation_wizard.xml',
    ],
    'assets': {
            'web.assets_backend': [
                'custom_guest_house/static/src/js/boolean_widget.js',
                'custom_guest_house/static/src/xml/boolean_widget.xml'
                ]
    },
    'application': True,
    'installable': True,
    'auto_install': False,
}
