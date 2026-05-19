# -*- coding: utf-8 -*-
{
    'name': "Shipment Tracker",
    'summary': """ This App will show the logistics shipments in a read only kanban view.""",
    'description': """This App will show the logistics shipments in a read only kanban view.""",
    'author': "AliFaleh @ Integrated Path",
    'website': "http://www.int-path.com",
    'category': 'Tracking',
    'version': '18.0.0.0',
    'depends': ['base','logistics'],
    'data': [
        'security/security.xml',
        'views/views.xml',
    ],
}
