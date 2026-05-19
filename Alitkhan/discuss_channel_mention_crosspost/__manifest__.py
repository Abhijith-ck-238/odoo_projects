{
    'name': 'Discuss Channel Mention Crosspost',
    'version': '1.0',
    'category': 'Productivity/Discuss',
    'summary': 'Send a copy of a message to a mentioned channel.',
    'description': """
        Restores the ability to cross-post a message to a Discuss channel 
        by mentioning the channel name with a hashtag (e.g., #general) in the chatter.
    """,
    'depends': ['mail'],
    'data': [
        'views/discuss_channel_views.xml',
    ],
    'installable': True,
    'application': False,
    'license': 'LGPL-3',
}
