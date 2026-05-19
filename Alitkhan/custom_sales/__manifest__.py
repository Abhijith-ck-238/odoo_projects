# -*- coding: utf-8 -*-
{
    'name': "Custom Sales Delivery",

    'summary': """
                    1.Delivery - Cutomize operations tab.
                    2.Sale Report - Showing  sale report according to sales team 
                    of logged in user if the user in (Sales Users (Sales Report))
                     group.
                    3.Creating contract from sale order.
                    """,

    'description': """ Adding sub items to operations tab with section label as main 
                       product name """,

    'author': "",
    'website': "",
    'category': 'sales',
    'version': '18.0.0.1',
    'sequence': 1,

    # any module necessary for this one to work correctly
    'depends': ['sale_management', 'sale_stock', 'stock', 'web','sale',
                'account','itkan_offering','project','itkan_custom_sales_order','custom_helpdesk','contracts'],

    # always loaded
    'data': [
        'data/user_groups.xml',
        'data/server_action.xml',
        'data/sale_order_data.xml',
        'data/sale_order_activity.xml',
        'data/sale_order_template.xml',
        # 'views/webclient_templates.xml',
        'views/stock_picking.xml',
        'views/sale_order_line.xml',
        'views/sale_order_views.xml',
        'views/account_move.xml',
        'views/res_config.xml',
        'report/storz_report.xml',
        'report/report_storz_exchange_template.xml',
        'report/custom_picking_operations.xml',
        # 'report/custom_sales_report.xml',
        # 'report/custom_report_deliveryslip.xml',
        'report/custom_sales_report_overdue.xml',
        'report/custom_sales_report_overdue_pdf.xml',
        'report/custom_sales_report_overdue_pdf_template.xml',
        'report/supplier_report.xml',
        'report/report_saleorder_document_inherit.xml',
],
    'assets': {
        'web.assets_backend': [
            "custom_sales/static/src/js/action_manager.js",
        ],
    },
    'application': True,
    'installable': True,
    'auto_install': False,
}
