# -*- coding: utf-8 -*-
# from odoo import http


# class LotSelectionExtension(http.Controller):
#     @http.route('/lot_selection_extension/lot_selection_extension/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/lot_selection_extension/lot_selection_extension/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('lot_selection_extension.listing', {
#             'root': '/lot_selection_extension/lot_selection_extension',
#             'objects': http.request.env['lot_selection_extension.lot_selection_extension'].search([]),
#         })

#     @http.route('/lot_selection_extension/lot_selection_extension/objects/<model("lot_selection_extension.lot_selection_extension"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('lot_selection_extension.object', {
#             'object': obj
#         })
