{
    'name': 'Custom Expenses abudget appproval',
    'category': 'Accounting/Expenses',
    'sequence': 10,
    'summary': 'Budget in Expenses',
    'description': """
            This module is used to add Budget to Expenses 
    """,
    'website': '',
'depends': [
        'base',
        'hr_expense',
        'hr_timesheet',
        'project',
        'analytic',
        'account_budget',
        'contracts',
        # 'product',
        'custom_sales',
        'leave_approver',
        'custom_employees',
        'account',
        'account_contracts_relation'
    ],
    'data': [
        'security/ir.model.access.csv',
        'security/custom_ir_rule.xml',
        'data/budget_deadline_notification.xml',
        'data/email_template.xml',

		'views/analytic_account.xml',
		'views/custom_budget_analytic.xml',
		'views/hr_employee.xml',
		'views/hr_expense_sheet.xml',
		'views/hr_expense.xml',
        'views/res_config_settings.xml',
],
# 'web.assets_backend': [
#             'custom_expense_budget_approval/static/src/**/*',
#         ],
    # 'assets': {
    #     'web.assets_backend': [
    #         # 'custom_expense_budget_approval/static/src/components/analytic_distribution/analytic_distribution.js',
    #         'custom_expense_budget_approval/static/src/components/analytic_distribution/analytic_distribution.xml',
    #     ]
    # },
    'installable': True,
    'application': True,
    'license': 'LGPL-3',
}
