# -*- coding: utf-8 -*-
{
    'name': "Tech Policies",

    'summary': """ """,

    'description': """
                    
                   """,

    'author': "",
    'website': "",
    'category': 'Uncategorized',
    'version': '18.0.1.0.0',
    'sequence': 1,

    # any module necessary for this one to work correctly
    'depends': ['base'],

    # always loaded
    'data': [
        'security/user_group.xml',
        'security/ir.model.access.csv',
        'data/tech_policies_squence.xml',
        'views/tech_policies_views.xml',
        'views/import_tech_policies_views.xml',
    ],
    'application': True,
    'installable': True,
    'auto_install': False,

}
