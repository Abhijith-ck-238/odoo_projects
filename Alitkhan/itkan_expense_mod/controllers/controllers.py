# -*- coding: utf-8 -*-
# from odoo import http


# class ItkanExpenseMod(http.Controller):
#     @http.route('/itkan_expense_mod/itkan_expense_mod/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/itkan_expense_mod/itkan_expense_mod/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('itkan_expense_mod.listing', {
#             'root': '/itkan_expense_mod/itkan_expense_mod',
#             'objects': http.request.env['itkan_expense_mod.itkan_expense_mod'].search([]),
#         })

#     @http.route('/itkan_expense_mod/itkan_expense_mod/objects/<model("itkan_expense_mod.itkan_expense_mod"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('itkan_expense_mod.object', {
#             'object': obj
#         })
