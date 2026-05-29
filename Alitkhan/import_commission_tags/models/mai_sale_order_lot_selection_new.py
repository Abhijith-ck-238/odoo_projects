import xlrd
from odoo import fields, models
import tempfile
import binascii
from odoo.exceptions import UserError
import xlsxwriter
import json


class ImportCommission(models.Model):
    _name = 'mai.sale.order.lot.selection.model'

    file_to_upload = fields.Binary('File')
    select_value = fields.Selection([
        ('sale_order_line', 'sale_order_line'),
        ('stock_move', 'stock_move'),
    ], String="Model")

    def sale_order_line(self, sheet):
        for row in range(sheet.nrows):
            if row >= 1:
                row_values = sheet.row_values(row)
                print(row_values)
                object = self.env['sale.order.line'].search(
                    [('id', '=', row_values[0])])
                object.sudo().write({'lot_id': False if row_values[
                                                            1] == 'False' else
                row_values[1]})

    def stock_move(self, sheet):
        for row in range(sheet.nrows):
            if row >= 1:
                row_values = sheet.row_values(row)
                print(row_values)
                object = self.env['stock.move'].search(
                    [('id', '=', row_values[0])])
                object.sudo().write({'lot_id': False if row_values[
                                                            1] == 'False' else
                row_values[1]})
                print(object)

    def action_custom_sale_order(self):
        fp = tempfile.NamedTemporaryFile(delete=False, suffix=".xlsx")
        fp.write(binascii.a2b_base64(self.file_to_upload))
        fp.seek(0)
        values = {}
        workbook = xlrd.open_workbook(fp.name)
        sheet = workbook.sheet_by_index(0)
        lines = []
        if self.select_value == 'stock_move':
            self.stock_move(sheet)
        if self.select_value == 'sale_order_line':
            self.sale_order_line(sheet)

    def cron_custom_sale_order(self):
        temp = self.env['sale.order.line'].search([])
        workbook = xlsxwriter.Workbook(
            '/home/cybrosys/Videos/mai_sale_order_lot_selection/sale_order_line.xlsx')
        worksheet = workbook.add_worksheet()
        row = -1
        for rec in temp:
            row = row + 1
            worksheet.write(row, 0, str(rec.id))
            worksheet.write(row, 1, str(rec.lot_id.id))
        workbook.close()
        temp = self.env['sale.order.line'].search([])
        workbook = xlsxwriter.Workbook(
            '/home/cybrosys/Videos/mai_sale_order_lot_selection/stock_move.xlsx')
        worksheet = workbook.add_worksheet()
        row = -1
        for rec in temp:
            row = row + 1
            worksheet.write(row, 0, str(rec.id))
            worksheet.write(row, 1, str(rec.lot_id.id))
        workbook.close()
