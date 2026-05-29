# -*- coding: utf-8 -*-
{
    'name': "Service Reports",

    'summary': """
    Service Report - Customizations
      """,

    'description': """
        1.Customization on service report.
        2. Added default value 'HH:MM AM/PM' to 'time_from' and 'time_to' field on the service.report.line.
        3. Added new menu 'Travelling Data' and fetch value to 'distance' field on service.report.timeline from travelling
         data.
    """,

    'author': " Cybrosys Technologies",
    'website': "",
    'category': 'Uncategorized',
    'version': '18.0.1.0.0',
    'application': False,

    # any module necessary for this one to work correctly
    'depends': ['service_reports', 'custom_contract'],

    'web.report_assets_common': [
        'custom_service_reports/static/src/css/custom_main.css',
    ],
    'assets': {
            'web.assets_frontend': [
                'service_reports/static/src/css/main.css',
            ],
        },

    # always loaded
    'data': [
        'data/sequence.xml',
        'security/res_groups.xml',
        'security/ir.model.access.csv',
        'views/service_report_view.xml',
        'views/service_report_cpmany_view.xml',
        'report/service_report.xml',
    ],
}
