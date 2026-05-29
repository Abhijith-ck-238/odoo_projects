# -*- coding: utf-8 -*-
# from odoo import http


# class DxInvoiceReport(http.Controller):
#     @http.route('/dx_invoice_report/dx_invoice_report/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/dx_invoice_report/dx_invoice_report/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('dx_invoice_report.listing', {
#             'root': '/dx_invoice_report/dx_invoice_report',
#             'objects': http.request.env['dx_invoice_report.dx_invoice_report'].search([]),
#         })

#     @http.route('/dx_invoice_report/dx_invoice_report/objects/<model("dx_invoice_report.dx_invoice_report"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('dx_invoice_report.object', {
#             'object': obj
#         })
