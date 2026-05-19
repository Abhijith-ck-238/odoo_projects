# -*- coding: utf-8 -*-
# from odoo import http


# class ResPartnerExtension(http.Controller):
#     @http.route('/res_partner_extension/res_partner_extension/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/res_partner_extension/res_partner_extension/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('res_partner_extension.listing', {
#             'root': '/res_partner_extension/res_partner_extension',
#             'objects': http.request.env['res_partner_extension.res_partner_extension'].search([]),
#         })

#     @http.route('/res_partner_extension/res_partner_extension/objects/<model("res_partner_extension.res_partner_extension"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('res_partner_extension.object', {
#             'object': obj
#         })
