{
    'name': 'Custom Planning',
    'description': "Customizations on planning",
    'category': 'Human Resources/Planning',
    'author': "Cybrosys Technologies",
    'version': '18.0.1.0.0',
    'summary': 'Planning Customizations',
    'description': """
           1. Customizations on planning.
    """,
    'website': '',
    'depends': ['planning', 'mail'],
    'data': [
        'data/planning_activity.xml',
        'views/planning_view.xml',
    ],

    'installable': True,
    'application': False,
    'auto_install': False,
    'license': 'LGPL-3',

}
