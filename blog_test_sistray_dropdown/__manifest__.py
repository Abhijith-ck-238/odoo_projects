# -*- coding: utf-8 -*-
{
    'name': 'Blog Test Sistray Dropdown',
    'version': "19.0.1.0.0",
    'summary': 'Brief description of the module',
    'description': '''
        Detailed description of the module
    ''',
    'category': 'Uncategorized',
    'author': 'Cybrosys Techno Solutions',
    'company': 'Cybrosys Techno Solutions',
    'maintainer': 'Cybrosys Techno Solutions',
    'website': 'https://www.cybrosys.com',
    'depends': ['base', 'mail'],
    'assets': {'web.assets_backend':
        [
            'blog_test_sistray_dropdown/static/src/js/systray_dropdown.js',
            'blog_test_sistray_dropdown/static/src/xml/systray_dropdown.xml',
        ]
    },
    'license': 'LGPL-3',
    'installable': True,
    'application': False,
    'auto_install': False,
}
