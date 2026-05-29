# -*- coding: utf-8 -*-
{
    'name': "Custom AL-ITKAN Extension",

    'summary': """
        Custom Itkan Extension
    """,

    'description': """
        A Module Developed by Integerated Path.
    """,
    'author': "ALITKAN ",
    'website': "https://alitkan.com/",
    'category': 'Uncategorized',
    'version': '18.0.1.0.0',
    'depends': ['base', 'hr_recruitment', 'al-itkan'],

    'data': [
        'views/hr_applicant_views.xml',
        'views/res_config_views.xml',
        'report/applicant_report.xml',
        'views/hr_job_views.xml',
    ],
    'application': True,
    'installable': True,
    'auto_install': False,
}
