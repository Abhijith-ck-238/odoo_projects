# from odoo import models, api
#
# class StockMoveLine(models.Model):
#     _inherit = "stock.move.line"
#
#
#     @api.model_create_multi
#     def create(self, vals_list):
#         res = super().create(vals_list)
#         # for res in res_list:
#         if res.picking_id.picking_type_code == 'incoming':
#             stock_quant = self.env['stock.quant'].search([
#                 ('product_id', '=', res.product_id.id),
#                 ('quantity', '>', 0),
#                 ('location_id.usage', '=', 'internal')
#             ], order='id DESC', limit=1)
#             if stock_quant:
#                 print('stock_quant',stock_quant.location_id.id)
#                 res.sudo().write({'location_dest_id': stock_quant.location_id.id})
#         return res
# from odoo import fields, models, api
#
#
# class StockMoveLine(models.Model):
#     _inherit = "stock.move.line"
#
#     @api.model
#     def create(self, vals):
#         res = super(StockMoveLine, self).create(vals)
#         if 'picking_id' in vals:
#             picking = self.env['stock.picking'].browse(vals['picking_id'])
#             if picking.picking_type_code == 'incoming' and 'product_id' in vals:
#                 stock_quant = self.env['stock.quant'].search([
#                     ('product_id', '=', vals['product_id']),
#                     ('quantity', '>', 0),
#                     ('location_id.usage', '=', 'internal')
#                 ], order='id DESC', limit=1)
#                 if stock_quant:
#                     vals['location_dest_id'] = stock_quant.location_id
#         print(res.read(),'res.......')
#         return res
