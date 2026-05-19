# -*- coding: utf-8 -*-
{
    'name': "Itkan - Preventive Maitainence",

    'summary': """ Automated preventive Maitainence Helpdesk ticket creation """,

    'description': """
        This Module is created for Al-ITkan, the module handles preventive maintainence using their contracts
        Module by automatically creating helpdesk ticket dependign on multiple criterias such as PAC date and EOC date.
        The app uses device S.N to pull relevant dates from the 'contracts' app and then creates a PM schedule that creates
        a helpdesk ticket in time.
    """,

    'author': "Ahmed Naseem",
    'website': "http://www.int-path.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/13.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Helpdesk',
    'version': '18.0.1.0.0',

    # any module necessary for this one to work correctly
    'depends': ['base', 'mail', 'contracts', 'itkan_helpdesk'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/views.xml',
        'views/contract_contract_views.xml',
        'views/preventive_maintainence_views.xml',
        'data/scheduled_action.xml'
    ],
}
