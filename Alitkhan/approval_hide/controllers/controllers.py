# -*- coding: utf-8 -*-
# from odoo import http


# class ApprovalHide(http.Controller):
#     @http.route('/approval_hide/approval_hide/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/approval_hide/approval_hide/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('approval_hide.listing', {
#             'root': '/approval_hide/approval_hide',
#             'objects': http.request.env['approval_hide.approval_hide'].search([]),
#         })

#     @http.route('/approval_hide/approval_hide/objects/<model("approval_hide.approval_hide"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('approval_hide.object', {
#             'object': obj
#         })
