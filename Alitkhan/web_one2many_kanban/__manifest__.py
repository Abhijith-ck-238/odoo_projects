# Copyright 2016 Serpent Consulting Services Pvt. Ltd
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    "name": "Web One2many Kanban",
    "version": "18.0.1.0.1",
    "license": "AGPL-3",
    "sequence": 6,
    "author": "Serpent Consulting Services Pvt. Ltd.",
    "maintainer": "Serpent Consulting Services Pvt. Ltd.",
    "website": "http://www.serpentcs.com",
    "summary": "Display one2many widget as kanban",
    "description": " ",
    "depends": ["web"],
    'assets': {
                'web.assets_backend': [
                        "web_one2many_kanban/static/src/js/web_one2many_kanban.js",
                        "web_one2many_kanban/static/src/xml/web_one2many_kanban.xml",
                ]
        },
    "images": ["static/description/o2mKanban.png"],
    "installable": True,
    "application": True,
}
