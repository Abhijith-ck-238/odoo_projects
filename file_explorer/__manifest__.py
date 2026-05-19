# -*- coding: utf-8 -*-
#############################################################################
#
#    Cybrosys Technologies Pvt. Ltd.
#
#    Copyright (C) 2025-TODAY Cybrosys Technologies(<https://www.cybrosys.com>).
#    Author: Afthab K Naufal @cybrosys (odoo@cybrosys.com)
#
#    You can modify it under the terms of the GNU AFFERO
#    GENERAL PUBLIC LICENSE (LGPL v3), Version 3.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU AFFERO GENERAL PUBLIC LICENSE (LGPL v3) for more details.
#
#    You should have received a copy of the GNU AFFERO GENERAL PUBLIC LICENSE
#    (LGPL v3) along with this program.
#    If not, see <http://www.gnu.org/licenses/>.
#
#############################################################################
{
    'name': 'File Explorer',
    'version': '18.0.1.0.0',
    'summary': 'Upload to server and download files from remote',
    'description': """ File Explorer is a file management module that enables seamless interaction 
            between your Odoo instance and remote servers.
            Key Features:
            - Remote Server Connection: Connect to remote servers by providing the host, 
              username, password, and port credentials directly from Odoo.
            - Directory Browsing: Navigate and browse directories on the remote server 
              through a simple dashboard interface.
            - File Upload: Upload files from your local machine to the connected remote 
              server with ease.
            - File Download: Download files from the remote server directly to your 
              local system.
            
            This module is compatible with both Community and Enterprise editions of Odoo 18. """,
    'category': 'Tools',
    'author': "Cybrosys Techno Solutions",
    'company': "Cybrosys Techno Solutions",
    'maintainer': "Cybrosys Techno Solutions",
    'website': "https://www.cybrosys.com",
    'depends': ['base', 'website', 'board'],
    'data': [
        'views/file_explorer_views.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'file_explorer/static/src/js/upload_file.js',
            'file_explorer/static/src/js/file_explorer.js',
            'file_explorer/static/src/xml/upload_file.xml',
            'file_explorer/static/src/xml/file_explorer.xml',
            'file_explorer/static/src/scss/upload_file.scss',
            'file_explorer/static/src/scss/file_explorer.scss',
        ],
    },
    'images': ['static/description/banner-01.jpg'],
    'license': 'AGPL-3',
    'installable': True,
    'auto_install': False,
    'application': True,
}
