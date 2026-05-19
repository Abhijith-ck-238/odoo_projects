# -*- coding: utf-8 -*-
{
    'name': "Custom Time off",

    'summary': """ Customizations on time off """,

    'description': """ 1. Added new group officer
                       2. Added new validation types to time off type
                       3. Approval notification for each validation types (both 
                       activity notification and discuss channel messages)""",

    'author': "",
    'website': "",
    'category': 'Human Resources/Time Off',
    'version': '18.0.0.1',
    'sequence': 1,

    # any module necessary for this one to work correctly
    'depends': ['base', 'hr_holidays', 'leave_approver', 'custom_employees','custom_sales'],

    # always loaded
    'data': [
        'security/custom_groups.xml',
        'security/ir.model.access.csv',
        'security/custom_rules.xml',
        'data/time_off_request_notification_channel.xml',
        'data/custom_activity.xml',
        'views/custom_hr_holiday_views.xml',
        'views/custom_hr_leave_type_views.xml',
        'views/custom_hr_leave.xml',
        'views/action_bypass_approval.xml',
        'views/hr_employee.xml',
    ],
    'application': True,
    'installable': True,
    'auto_install': False,
}
