# -*- coding: utf-8 -*-
# from odoo import http


# class ItkanBankExt(http.Controller):
#     @http.route('/itkan_bank_ext/itkan_bank_ext/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/itkan_bank_ext/itkan_bank_ext/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('itkan_bank_ext.listing', {
#             'root': '/itkan_bank_ext/itkan_bank_ext',
#             'objects': http.request.env['itkan_bank_ext.itkan_bank_ext'].search([]),
#         })

#     @http.route('/itkan_bank_ext/itkan_bank_ext/objects/<model("itkan_bank_ext.itkan_bank_ext"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('itkan_bank_ext.object', {
#             'object': obj
#         })
