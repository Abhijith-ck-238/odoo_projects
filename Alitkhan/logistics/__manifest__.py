# -*- coding: utf-8 -*-
{
    'name': "Logsitics",
    'summary': """This app is used to manager all the aspects of the Logistic process including creation of shipment, shipping expenses, tracking routes, documents and status""",
    'description': """This app is used to manager all the aspects of the Logistic process including creation of shipment, shipping expenses, tracking routes, documents and status""",
    'author': "AhmedNaseem and AliFaleh @ Integrated Path",
    'website': "http://www.yourcompany.com",
    'category': 'logistics',
    'version': '0.1',
    'depends': ['base', 'purchase', 'contracts', 'offering_purchase_order'],
    # offering purchase order added because it depends on contract_id from there.
    'data': [
        'security/ir.model.access.csv',
        'views/views.xml',
        'views/logistics_view.xml',
        'views/purchase_order_inh_views.xml',
        'views/shipment_route_views.xml',
        'views/shipment_document_views.xml',
        'views/shipment_stage_view.xml',
        'data/sequence_data.xml',
        'security/groups.xml'
    ],
    'assets': {
        'web.assets_backend': [
            'logistics/static/src/css/kanban.css',
            'logistics/static/src/css/style.css',
            'logistics/static/src/js/many2many.js',
            'logistics/static/src/js/many2many.xml',
            'logistics/static/src/js/purchase_order_popup.js',
        ],
    },

}
