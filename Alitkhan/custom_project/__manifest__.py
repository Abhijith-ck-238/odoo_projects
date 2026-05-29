# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'CUSTOM PROJECT',
    'version': '1.1',
    'website': 'https://exploit-consult.com',
    'category': 'Operations/Project',
    'sequence': 10,
    'summary': 'customization for module project',
    'depends': [
        'project',
        'base_setup',
    ],
    'description': "",
    'data': [
        #"security/security.xml",
        "security/ir.model.access.csv",
        'views/project_task_view.xml',
        'views/project_view.xml',
        'views/project_template_view.xml',

    ],
    'demo': [],
    'test': [
    ],
    'installable': True,
    'auto_install': False,
    'application': True,
}
