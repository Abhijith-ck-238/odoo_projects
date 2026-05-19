{
    "name": "Your Module Name",
    "version": "19.0.1.0.0",
    "summary": "",
    "description": """
    """,
    "author": "Your Name",
    "website": "https://yourwebsite.com",
    "category": "Tools",
    "depends": ["web"],
    "data": [
         "views/your_module_actions.xml"
    ],
    "assets": {
        "web.assets_backend": [
            "useExternalListener_blog/static/src/components/components.xml",
            "useExternalListener_blog/static/src/components/components.js",
        ],
    },
    "installable": True,
    "application": False,
    "license": "LGPL-3",
}
