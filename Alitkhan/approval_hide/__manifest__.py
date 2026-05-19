# -*- coding: utf-8 -*-
{
    'name': "Approvals Access Control",

    'summary': """
        This Module is used to add a functionality that enables admin to hide approval categories depending on user ids""",

    'description': """
       This Module is used to add a functionality that enables admin to hide approval categories depending on user ids
    """,

    'author': "Ahmed Naseem",
    'website': "http://www.int-path.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/13.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','approvals'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/views.xml',
        'views/templates.xml',
        'views/approval_views.xml',
        'data/approvals_rule.xml'


        
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
