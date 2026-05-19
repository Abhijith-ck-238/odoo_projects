{
    'name': "Custom Survey",
    'summary': "Custom Survey Extensions",
    'description': "Custom Survey module with sum calculation",
    'author': "",
    'website': "",
    'category': 'Survey',
    'version': '18.0.1.0.0',
    'sequence': 1,
    'license': 'LGPL-3',

    'depends': ['base', 'web', 'survey'],

    'assets': {
        'survey.survey_assets': [
            'custom_survey/static/src/js/survey.js',
        ]
    },

    'data': [
        'views/survey_templates.xml',
    ],

    'application': True,
    'installable': True,
    'auto_install': False,
}
