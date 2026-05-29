# -*- coding: utf-8 -*-
{
    'name': "Confirm On Status Change",
    'summary': """This module will require the user to confirm before changing the status of any record.""",
    'description': """This module will require the user to confirm before changing the status of any record.""",
    'author': "AliFaleh",
    'website': "http://www.int-path.com",
    'category': 'Confirmation',
    'version': '18.0.0.0',
    'depends': ['base'],
    'assets': {
        'web.assets_backend': [
            'confirm_on_status_change/static/src/js/kanban_view_confirmation.js',
        ],
    },
}
