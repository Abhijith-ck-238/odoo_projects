# -*- coding: utf-8 -*-
{
    'name': "Custom Attachment Preview",
    'summary': "Preview attachments directly in Odoo.",
    'description': """This module allows users to preview document attachments within Odoo.""",
    'author': "",
    'website': "",
    'category': 'Documents',
    'version': '18.0.0.1',
    'sequence': 1,
    'license': 'LGPL-3',

    # Dependencies
    'depends': ['base', 'web'],


    'data': [
        'views/attachment_preview.xml',
    ],

    'assets': {
        'web.assets_backend': [
            'custom_attchement_preview/static/src/xml/attachment_preview.xml',
            'custom_attchement_preview/static/src/js/attachment_preview.js',
        ],
    },

    'application': True,
    'installable': True,
    'auto_install': False,
}
