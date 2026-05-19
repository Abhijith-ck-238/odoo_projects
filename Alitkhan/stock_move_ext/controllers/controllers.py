# -*- coding: utf-8 -*-
# from odoo import http


# class StockMoveExt(http.Controller):
#     @http.route('/stock_move_ext/stock_move_ext/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/stock_move_ext/stock_move_ext/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('stock_move_ext.listing', {
#             'root': '/stock_move_ext/stock_move_ext',
#             'objects': http.request.env['stock_move_ext.stock_move_ext'].search([]),
#         })

#     @http.route('/stock_move_ext/stock_move_ext/objects/<model("stock_move_ext.stock_move_ext"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('stock_move_ext.object', {
#             'object': obj
#         })
