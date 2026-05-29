{
    'name': 'Rare ORM Method Blog (Odoo 19)',
    'version': '1.0',
    'category': 'Healthcare',
    'summary': 'Demonstration of name_get, display_name, and name_search in Odoo 19',
    'description': """
        This module tests the concepts described in the Rare ORM Method Blog:
        - Modern display_name computation.
        - Backward compatibility with name_get().
        - Syncing search with display using name_search() with domain parameter.
    """,
    'author': 'Antigravity',
    'depends': ['base'],
    'data': [
        'security/ir.model.access.csv',
        'views/hospital_ward_views.xml',
        'views/hospital_patient_views.xml',
        'views/hospital_menus.xml',
    ],
    'installable': True,
    'application': True,
    'license': 'LGPL-3',
}
