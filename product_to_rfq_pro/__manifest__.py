# -*- coding: utf-8 -*-
###############################################################################
#
#    Cybrosys Technologies Pvt. Ltd.
#
#    Copyright (C) 2026-TODAY Cybrosys Technologies(<https://www.cybrosys.com>)
#    Author: Abhijith CK (odoo@cybrosys.com)
#
#    This program is under the terms of the Odoo Proprietary License v1.0(OPL-1)
#    It is forbidden to publish, distribute, sublicense, or sell copies of the
#    Software or modified copies of the Software.
#
#    THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#    IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#    FITNESS FOR A PARTICULAR PURPOSE AND NON INFRINGEMENT.
#    IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM,
#    DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR
#    OTHERWISE,ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE
#    USE OR OTHER DEALINGS IN THE SOFTWARE.
#
###############################################################################
{
    'name': 'Add Multiple Products To RFQ Pro',
    'version': '18.0.1.0.0',
    'category': 'Purchases',
    'sequence': 1,
    'summary': """Now you can add multiple products to purchase RFQ (Request 
     for Quotation) form much easier than ever with new feature.""",
    'description': """We streamline the process of adding multiple products to
    the corresponding purchase request for quotation (RFQ). Our solution
    provides a user-friendly interface with kanban, list, and form views for
    easy product management. Additionally, it displays the previous purchase
    history of selected products and RFQs, allows for the creation of multiple
    RFQs, enables salespeople to add RFQs, and offers a convenient button within
    the purchase request for quotation interface for quickly adding products
    directly to the RFQ and select multiple products simultaneously, enhancing
    efficiency and usability.""",
    'author': 'Cybrosys Techno Solutions',
    'company': 'Cybrosys Techno Solutions',
    'maintainer': 'Cybrosys Techno Solutions',
    'website': 'https://www.cybrosys.com',
    'depends': ['purchase'],
    'data': [
        'security/ir.model.access.csv',
        'views/product_product_views.xml',
        'views/purchase_order_views.xml',
        'wizard/product_to_rfq_views.xml',
    ],
    'demo': [],
    'images': ['static/description/banner.jpg'],
    'license': 'OPL-1',
    'price': 49.99,
    'currency': 'EUR',
    'installable': True,
    'auto_install': False,
    'application': False,
}
