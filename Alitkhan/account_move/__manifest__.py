# -*- coding: utf-8 -*-
{
    'name': "Accounting Bill",

    'summary': """Account - Create Bill """,

    'description': """ Create bill for remaining lines to be billed purchase order """,

    'author': "",
    'website': "",
    'category': 'Accounting',
    'version': '18.0.1.0',
    'sequence': 1,

    # any module necessary for this one to work correctly
    'depends': ['base', 'account', 'purchase', 'custom_sales','itkan_report_mod','account_accountant'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/account_move.xml',
        'views/account_payment.xml',
        'views/bank_rec_widget_views.xml',
        'wizard/link_purchase.xml',
        'wizard/warning_wizard.xml',
        'reports/custom_report_payment_receipt.xml',
        'reports/custom_invoice_report_copy.xml',
        'reports/invoice_report_template.xml',
        'reports/custom_invoice_preforma_report.xml',
        'reports/custom_report_document.xml',
        'reports/custom_report_name.xml',
    ],
    'assets': {
        'web.report_assets_common': [
            'account_move/static/src/scss/primary_variable.scss',
            'account_move/static/src/scss/report_style.scss'
        ],
    },
    'application': True,
    'installable': True,
    'auto_install': False,
}
