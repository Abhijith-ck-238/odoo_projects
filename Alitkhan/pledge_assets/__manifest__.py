# -*- coding: utf-8 -*-
{
    'name': "Pledge Management",
    'summary': "For Creating & Managing Pledges",
    'author': "Integrated Path",
    'website': "https://www.int-path.com",
    'category': 'Uncategorized',
    'version': '18.0.1.0.0',
    'license': 'LGPL-3',
    'application': True,
    'installable': True,

    # Dependencies (ensure compatibility with Odoo 18)
    'depends': ['base', 'mail', 'contacts',"contracts"],

    # Data files
    'data': [
        'security/res_groups_data.xml',
        'security/ir.model.access.csv',
        'views/pledge_pledge_views.xml',
        'views/pledge_bank_views.xml',
        'views/res_partner_view.xml',
        'views/views.xml',
        'views/res_config_view.xml',
        'data/ir_cron.xml',
        'data/ir_sequence.xml',
    ],
}
