# -*- coding: utf-8 -*-
# from odoo import http


# class SaleOrderReportLotOptional(http.Controller):
#     @http.route('/sale_order_report_lot_optional/sale_order_report_lot_optional/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/sale_order_report_lot_optional/sale_order_report_lot_optional/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('sale_order_report_lot_optional.listing', {
#             'root': '/sale_order_report_lot_optional/sale_order_report_lot_optional',
#             'objects': http.request.env['sale_order_report_lot_optional.sale_order_report_lot_optional'].search([]),
#         })

#     @http.route('/sale_order_report_lot_optional/sale_order_report_lot_optional/objects/<model("sale_order_report_lot_optional.sale_order_report_lot_optional"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('sale_order_report_lot_optional.object', {
#             'object': obj
#         })
