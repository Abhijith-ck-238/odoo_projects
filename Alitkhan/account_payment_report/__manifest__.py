{
    'name': 'General Payment Report',
    'version': '18.0.1.0.0',
    'category': 'Accounting/Accounting',
    'summary': 'Comprehensive SQL Report for Bank and Cash Payments',
    'description': """
        This module provides a comprehensive report for all money inflows and outflows
        across bank and cash journals, including links to invoices, bills, and expense reports.
    """,
    'author': "cybrosys",
    'depends': ['account', 'hr_expense'],
    'data': [
        'security/ir.model.access.csv',
        'views/payment_report_views.xml',
    ],
    'installable': True,
    'application': False,
    'license': 'LGPL-3',
}
