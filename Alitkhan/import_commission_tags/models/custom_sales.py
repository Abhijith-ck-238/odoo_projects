import xlrd
from odoo import fields, models
import tempfile
import binascii
from odoo.exceptions import UserError
import xlsxwriter
import json




class ImportCommission(models.Model):
    _name = 'custom.sale.model'

    file_to_upload = fields.Binary('File')
    select_value = fields.Selection([('sale_order','sale_order'),
                                     ('sale_order_line', 'sale_order_line'),
                                     ('stock_move','stock_move'),
                                     ('stock_move_line','stock_move_line')

                                     ],String="Model")

    def sale_order(self, sheet):
        for row in range(sheet.nrows):
            if row >= 1:
                row_values = sheet.row_values(row)
                print(row_values)
                object = self.env['sale.order'].search([('id', '=', row_values[0])])
                object.is_to_print_subunit_pricing = row_values[1]
                object.total_of_exchange_products = row_values[2]
                object.select_all_lines = row_values[3]
                print(object)

    def sale_order_line(self, sheet):
        for row in range(sheet.nrows):
            if row >= 1:
                row_values = sheet.row_values(row)
                print(row_values)
                object = self.env['sale.order.line'].search([('id', '=', row_values[0])])
                object.config = False if row_values[1] == 'False' else row_values[1]
                object.is_exchange = row_values[2]
                print(object)

    def stock_move(self,sheet):
        for row in range(sheet.nrows):
            if row >= 1:
                row_values = sheet.row_values(row)
                print(row_values)
                object = self.env['stock.move'].search([('id', '=', row_values[0])])
                # object.sequence = False if row_values[1] == 'False' else row_values[1],
                object.display_type =False if row_values[2] == 'False' else row_values[2]
                print(object)

    def stock_move_line(self,sheet):
        for row in range(sheet.nrows):
            if row >= 1:
                row_values = sheet.row_values(row)
                print(row_values)
                object = self.env['stock.move.line'].search([('id', '=', row_values[0])])
                object.name = row_values[1],
                object.sequence = row_values[2]
                object.display_type = row_values[3]
                print(object)


    def action_custom_sale_order(self):
        fp = tempfile.NamedTemporaryFile(delete=False, suffix=".xlsx")
        fp.write(binascii.a2b_base64(self.file_to_upload))
        fp.seek(0)
        values = {}
        workbook = xlrd.open_workbook(fp.name)
        sheet = workbook.sheet_by_index(0)
        lines = []
        if self.select_value == 'sale_order':
            self.sale_order(sheet)
        if self.select_value == 'sale_order_line':
            self.sale_order_line(sheet)
        if self.select_value == 'stock_move':
            self.stock_move(sheet)
        if self.select_value == 'stock_move_line':
            self.stock_move_line(sheet)


    def cron_custom_sale_order(self):
        temp=self.env['sale.order'].search([])
        workbook = xlsxwriter.Workbook('/home/cybrosys/Videos/custom_sale/sale_order.xlsx')
        worksheet = workbook.add_worksheet()
        row=-1
        for rec in temp:
            row=row+1
            worksheet.write(row, 0, str(rec.id))
            worksheet.write(row, 1, str(rec.is_to_print_subunit_pricing))
            worksheet.write(row, 2, str(rec.total_of_exchange_products))
            worksheet.write(row, 3, str(rec.select_all_lines))
        workbook.close()
        temp=self.env['sale.order.line'].search([])
        workbook = xlsxwriter.Workbook('/home/cybrosys/Videos/custom_sale/sale_order_line.xlsx')
        worksheet = workbook.add_worksheet()
        row=-1
        for rec in temp:
            row=row+1
            worksheet.write(row, 0, str(rec.id))
            worksheet.write(row, 1, str(rec.config.id))
            worksheet.write(row, 2, str(rec.is_exchange))
        workbook.close()
        temp=self.env['stock.move'].search([])
        workbook = xlsxwriter.Workbook('/home/cybrosys/Videos/custom_sale/stock_move.xlsx')
        worksheet = workbook.add_worksheet()
        row=-1
        for rec in temp:
            row=row+1
            worksheet.write(row, 0, str(rec.id))
            worksheet.write(row, 1, str(rec.name))
            worksheet.write(row, 2, str(rec.sequence))
            worksheet.write(row, 2, str(rec.display_type))
        workbook.close()
        temp=self.env['stock.move.line'].search([])
        workbook = xlsxwriter.Workbook('/home/cybrosys/Videos/custom_sale/stock_move_line.xlsx')
        worksheet = workbook.add_worksheet()
        row=-1
        for rec in temp:
            row=row+1
            worksheet.write(row, 0, str(rec.id))
            worksheet.write(row, 0, str(rec.name))
            worksheet.write(row, 1, str(rec.sequence))
            worksheet.write(row, 2, str(rec.display_type))
        workbook.close()
