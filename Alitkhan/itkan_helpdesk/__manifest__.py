# -*- coding: utf-8 -*-
{
    'name': "Itkan Hepldesk Extension",

    'summary': """A module for apply the necesary customization for Al-Itkan's Helpdesk""",

    'author': "Integerated Path",
    'website': "https://www.int-path.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/13.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Support',
    'version': '18.0.0.1.0',

    # any module necessary for this one to work correctly
    'depends': ['base', 'helpdesk', 'contracts', 'service_reports', 'contacts', 'industry_fsm', 'project_stage_state',
                'itkan_fleet_customization', 'calendar', 'access_units', 'sale_project', 'sale_timesheet',
                'sale_stock'],

    # always loaded
    'data': [
        'data/fsm_data.xml',
        'security/ir.model.access.csv',
        "views/actions_views.xml",
        "views/helpdesk_ticket_view.xml",
        "views/helpdesk_stage_view.xml",
        "views/project_task_view.xml",
        "views/project_task_type_view.xml",
        "views/helpdesk_ticket_type_views.xml",
        # "views/res_users_view.xml",
        # "views/product_product_views.xml",
        "report/report_actions.xml",
        "data/resource_category_data.xml",
    ],

    'assets': {
        'web.assets_backend': [
            'itkan_helpdesk/static/src/js/action_manager.js'
        ]
    },
}
