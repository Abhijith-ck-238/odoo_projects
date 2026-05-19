# -*- coding: utf-8 -*-
{
    'name': "Custom Contract",

    'summary': """Customizations contract module""",

    'description': """ 1. Added Technical products to contracts.
                       2. Added button to show subunits.
                       3. Added Archive option on contracts and added filter Archived.
                       4. Added Peripherals
                   """,

    'author': "",
    'website': "",
    'category': 'Doccuments',
    'version': '18.0.0.1',
    'sequence': 1,

    # any module necessary for this one to work correctly
    'depends': ['contracts', 'offering_configuration', 'product', 'itkan_helpdesk', 'itkan_pm',
                'custom_training','account_contracts_relation','logistics','custom_helpdesk','board'],

    # always loaded
    'data': [
        'data/product_access_rule.xml',
        'security/ir.model.access.csv',
        'data/action_compute_is_eoc.xml',
        'data/action_compute_contract_in_warranty.xml',
        'reports/contract_report.xml',
        'views/company.xml',
        'views/product.xml',
        'views/contract_product_form_view.xml',
        'views/contract_product.xml',
        'views/contract_search_view.xml',
        'views/technical_product.xml',
        'wizards/config_wizard.xml',
        # 'views/offering_views.xml',
        'views/interval_view.xml',
        'views/contract_action.xml',
        'views/hr_department.xml',
        'views/compute_product_char.xml',
        'views/peripherals_view.xml',
        'views/health_department_view.xml',
        'views/contract_site_view.xml',
        'views/contract_contract.xml',
        'views/mail_channel_view.xml',
        'wizards/peripherals_wizard.xml',
        'wizards/contract_sub_line_wizard.xml',
    ],
    'application': True,
    'installable': True,
    'auto_install': False,

}
