# -*- coding: utf-8 -*-
{
    'name': "Taining",

    'summary': """ """,

    'description': """
                    
                   """,

    'author': "",
    'website': "",
    'category': 'Uncategorized',
    'version': '18.0.1.0.0',
    'sequence': 1,

    # any module necessary for this one to work correctly
    'depends': ['base','mail', 'hr_expense','documents', 'account_budget', 'purchase','custom_employees'],

    # always loaded
    'data': [
        'data/training_sequence.xml',
        'data/training_due_reminder_template.xml',
        'data/send_reminder_cron.xml',
        'data/budget_activity.xml',
        'security/user_group.xml',
        'security/ir.model.access.csv',
        'views/training_ticket.xml',
        'views/training_type.xml',
        'views/attendees_position.xml',
        'views/res_config_settings.xml',
        'views/training_stage.xml',
        'views/training_attendees.xml',
        'views/training_location.xml',
        'reports/training_report.xml',
        'views/hr_expense.xml',
    ],
    'application': True,
    'installable': True,
    'auto_install': False,

}
