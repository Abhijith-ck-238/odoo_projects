# -*- coding: utf-8 -*-
{
    'name': "Contract Attchment view",

    'summary': """
        Attachments that are not accssible is been hidden from the chatter""",

    'description': """
        Attachments that are not accssible is been hidden from the chatter
    """,

    'category': 'hr',
    'version': '18.0.0.1',
    'application': True,
    # any module necessary for this one to work correctly
    'depends': ['hr_contract', 'mail'],

    'assets': {
        'web.assets_backend': [
            'contract_chatter_attacment/static/src/js/attachment_list.js'
        ],
        'mail.assets_public': [
            'contract_chatter_attacment/static/src/js/attachment_list.js'
        ],
    }
}
