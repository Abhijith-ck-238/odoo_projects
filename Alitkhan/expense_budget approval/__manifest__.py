{
    'name': 'expense budget approval',
    'category': 'Accounting/Expenses',
    'sequence': 10,
    'summary': 'Budget in Expenses',
    'description': """
            This module is used to add budget and its approval 
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
        'custom_sales',
        'leave_approver',
        'custom_employees',
    ],
    'data': [
        'security/ir.model.access.csv',
        'security/custom_ir_rule.xml',
        'data/crossovered_budget_data.xml',
        'data/mail_template.xml',
        'view/employee_form_view_extend.xml',
        'view/custom_crossovered_budget_view.xml',
        'view/custom_expense_res_config_settings.xml',
        'view/analytic_account_view.xml',
        'view/res_config_settings.xml',
        'view/filter_views.xml',
        'view/hr_expense_view.xml',
        'view/attachment_view.xml'
    ],
    'installable': True,
    'application': True,
    'license': 'LGPL-3',
}
