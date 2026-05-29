# -*- coding: utf-8 -*-
{
    'name': "AL-ITKAN Extension",

    'summary': """
        Itkan Extension
    """,

    'description': """
        A Module Developed by Integerated Path
    """,

    'author': "Integerated Path",
    'website': "https://www.int-path.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/13.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '18.0.0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'hr_recruitment', 'product',  'hr','purchase',
                'mai_sale_order_lot_selection', 'access_units', 'contracts', 'product_expiry','hr_contract','sale_expense'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/views.xml',
        'views/expenses_sheet_view.xml',
        'views/product_view.xml',
        "views/employee_view.xml",
        "views/jobs_view.xml",
        "views/calendar_event_view.xml",
        "views/sale_order_view.xml",
        "views/prucahase_order_views.xml",
        "views/account_move_view.xml",
        "views/stock_quant_view.xml",
        "views/analytic_account_id_custom_tree.xml",
        "views/hr_recruitment_stage_view.xml",
        "views/hr_applicant_view.xml",
        "report/recruitment_report.xml",
        "report/external_layout_standard.xml",
        "data/expense_sheet_record_rule.xml",
        
    ],
    'css':['static/src/css/style.css'],
}
