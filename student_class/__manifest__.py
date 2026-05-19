#FOR BLOG TESTING
{
    'name': 'Student Class - Standalone OWL',
    'version': '1.0',
    'category': 'Hidden',
    'summary': 'Standalone OWL application test module',
    'description': """Testing a standalone OWL app inside Odoo 17.""",
    'depends': ['base', 'mail', 'web'],
    'data': [
        'security/ir.model.access.csv',
        'views/standalone_app.xml',
        'views/student_class_views.xml',
    ],
    'assets': {
        'student_class.assets_standalone_app': [
            ('include', 'web._assets_helpers'),
            'web/static/src/scss/pre_variables.scss',
            'web/static/lib/bootstrap/scss/_variables.scss',
            ('include', 'web._assets_bootstrap'),
            ('include', 'web._assets_core'),
            'student_class/static/src/standalone_app/**/*',
        ],
    },
    'installable': True,
    'application': True,
    'license': 'LGPL-3',
}
