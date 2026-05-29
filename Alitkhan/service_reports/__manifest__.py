# -*- coding: utf-8 -*-
{
    'name': "Service Reports",

    'summary': """
        Short (1 phrase/line) summary of the module's purpose, used as
        subtitle on modules listing or apps.openerp.com""",

    'description': """
        Long description of module's purpose
    """,

    'author': "Intgerated Path",
    'website': "https://www.int-path.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/13.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '18.0.1.0.0',
    'application': True,

    # any module necessary for this one to work correctly
    'depends': ['base', 'contracts', 'web'],


# 'assets': {
#         'web.report_assets_common': [
#             'service_reports/static/src/scss/main.scss',
#         ],
# },

# 'assets': {
#     'web.report_assets_common': [
#         '/service_reports/static/src/scss/main.scss',
#         # 'https://fonts.googleapis.com/css2?family=Lato:ital,wght@0,100;0,300;0,400;0,700;0,900;1,100;1,300;1,400;1,700;1,900&display=swap',
#     ],
# },

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/groups.xml',
        'views/views.xml',
        'views/service_report_view.xml',
        'reports/service_report.xml',

    ],
}
