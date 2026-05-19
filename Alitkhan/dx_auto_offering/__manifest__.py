# -*- coding: utf-8 -*-
{
    'name': "DX Auto Offering",
    'summary': """No summary til now""",
    'description': """No description til now""",
    'author': "AliFaleh @ Integerated Path",
    'application': True,
    'website': "https://www.int-path.com",
    'category': 'Sales',
    'version': '0.1',
    'depends': ['base', 'stock','hr'],
    'data': [
        'security/securety.xml',
        'security/ir.model.access.csv',
        'views/views.xml',
        'views/quotation_offer.xml',
        'views/qoutation_offer_template.xml',
        'report/report.xml',
        'report/dx_offer.xml',
        'data/sequence_data.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'dx_auto_offering/static/src/css/style.css',
            'dx_auto_offering/static/src/js/copy_on_click.js',
        ],
    },
    'license': 'LGPL-3',
}
