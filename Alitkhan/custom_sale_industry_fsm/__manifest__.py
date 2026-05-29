# -*- coding: utf-8 -*-
{
    'name': "Custom Industry Fsm",

    'summary': """Custom Industry Fsm """,

    'description': """ 1.Filter Fsm Products (show only the selected products when Products on the project.task clicked.
    If 0 item is selected, it shows all items.)""",

    'author': "",
    'website': "",
    'category': 'Operations/Field Service',
    'version': '18.0.0.0',
    'sequence': 1,

    # any module necessary for this one to work correctly
    'depends': ['custom_industry_fsm','itkan_helpdesk'],

    # always loaded
    'data': [
        'views/fsm_views.xml',
        'views/project_task.xml',
    ],
    'application': False,
    'installable': True,
    'auto_install': False,

}
