# -*- coding: utf-8 -*-
# Part of Sananaz Mansuri. See LICENSE file for full copyright and licensing details.

{
    'name': 'Journal Restricted Users',
    'version': '18.0.1.0.0',
    'category': 'Accounting',
    'price': 39.0,
    'currency': 'EUR',
    'summary': "Restrict Account Journals by Users",
    'description': """
        - Restricts account journal access based on assigned users.
        - Only assigned users can view or use specific journals.
        - Adds security rules to limit journal visibility.
    """,
    'author': "Probuse Consulting Service Pvt. Ltd.",
    'website': "https://www.probuse.com",
    'support': 'contact@probuse.com',
    'license': 'LGPL-3',
    'maintainers': ['probuse'],
    'depends': ['account'],
    'data': [
        'security/account_journal_security.xml',
        'views/account_journal_view.xml',
    ],

    'images': ['static/description/image.png'],
    'live_test_url': 'https://youtu.be/MLo-B1PkwSI',
    'installable': True,
    'application': True,
    'auto_install': False,
}
