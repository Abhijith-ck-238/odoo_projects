# -*- coding: utf-8 -*-
# from odoo import http


# class ItkanSearchpanel(http.Controller):
#     @http.route('/itkan_searchpanel/itkan_searchpanel/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/itkan_searchpanel/itkan_searchpanel/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('itkan_searchpanel.listing', {
#             'root': '/itkan_searchpanel/itkan_searchpanel',
#             'objects': http.request.env['itkan_searchpanel.itkan_searchpanel'].search([]),
#         })

#     @http.route('/itkan_searchpanel/itkan_searchpanel/objects/<model("itkan_searchpanel.itkan_searchpanel"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('itkan_searchpanel.object', {
#             'object': obj
#         })
