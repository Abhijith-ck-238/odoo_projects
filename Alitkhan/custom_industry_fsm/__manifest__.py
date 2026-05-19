# -*- coding: utf-8 -*-
{
    'name': "Custom Industry Fsm",

    'summary': """Custom Industry Fsm """,

    'description': """ 1.Filter Fsm Products (show only the selected products when Products on the project.task clicked.
    If 0 item is selected, it shows all items.)""",

    'author': "",
    'website': "",
    'category': 'Operations/Field Service',
    'version': '18.0.0.1',
    'sequence': 1,

    # any module necessary for this one to work correctly
    'depends': ['hr_timesheet', 'industry_fsm_report', 'project_timesheet_forecast', 'web','crm','access_units','logistics','industry_fsm','industry_fsm_stock'],

    # always loaded
    'data': [
        'security/res_groups.xml',
        'security/ir.model.access.csv',
        'data/field_service_sale_order.xml',
        'views/view_industry_fsm.xml',
        'views/search_view_fsm_industry.xml',
        'views/view_kanban_material.xml',
        'views/crm_lead_view.xml',
        'views/project_task_type_list_view.xml',
		'views/fsm_views.xml',
],
    'qweb': [
        "static/src/xml/kanban.xml"],
    'assets': {
        'web.assets_backend': [
            'custom_industry_fsm/static/src/product_catalog/order_line.js',
        ]
    },
    'application': False,
    'installable': True,
    'auto_install': False,

}
