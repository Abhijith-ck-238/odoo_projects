{
    'name': 'Order Line Count Widget',
    'version': '19.0.1.0.0',
    'summary': 'Custom view widget to display order line count and quantity',
    'description': 'A module testing the custom view widget for order line count.',
    'category': 'Hidden',
    'author': 'Test Author',
    'depends': ['purchase'],
    'data': [
        'views/purchase_order_view.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'order_line_count_widget/static/src/js/order_line_count_widget.js',
            'order_line_count_widget/static/src/xml/order_line_count_widget.xml',
        ],
    },
    'installable': True,
    'application': False,
    'license': 'LGPL-3',
}
