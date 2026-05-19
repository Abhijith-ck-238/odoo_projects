# -*- coding: utf-8 -*-
{
    'name': "ITKAN - Fleet Customization",

    'summary': """
        This Module is used to customize fleet Module """,

    'description': """
        Long description of module's purpose
    """,

    'author': "Ahmed Naseem",
    'website': "http://www.int-path.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/13.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '18.0.1.0.0',

    # any module necessary for this one to work correctly
    'depends': ['base','fleet','service_reports'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'data/groups.xml',
        'views/fleet_vehicle_view.xml',
        'views/fleet_vehicle_log_services.xml',
        'views/fleet_vehicle_model_category.xml',
    ],
}
