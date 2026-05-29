#FOR BLOG TESTING
{
    'name': 'CybroPay Payment Provider',
    'version': '1.0.0',
    'category': 'Accounting/Payment Providers',
    'depends': ['payment', 'account_payment'],
    'data': [
        'security/ir.model.access.csv',
        'views/payment_provider_views.xml',
        'views/payment_cybropay_templates.xml',
        'data/payment_method_data.xml',
        'data/payment_provider_data.xml',
    ],
    'assets': {
        'web.assets_frontend': [
            'payment_cybropay/static/src/js/payment_form.js',
            'payment_cybropay/static/src/xml/payment_cybropay_templates.xml',
        ],
    },
    'post_init_hook': 'post_init_hook',
    'uninstall_hook': 'uninstall_hook',
    'license': 'LGPL-3',
}
