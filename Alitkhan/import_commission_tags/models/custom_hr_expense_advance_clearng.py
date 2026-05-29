import xlrd
from odoo import fields, models
import tempfile
import binascii
from odoo.exceptions import UserError
import xlsxwriter
import json




class ImportCommission(models.Model):
    _name = 'custom.hr.expense.advance.clearng.model'

    file_to_upload = fields.Binary('File')
    select_value = fields.Selection([('hr_expense_sheet','hr_expense_sheet'),

                                     ],String="Model")

    def hr_expense_sheet(self, sheet):
        for row in range(sheet.nrows):
            if row >= 1:
                row_values = sheet.row_values(row)
                print(row_values)
                object = self.env['hr.expense.sheet'].search([('id', '=', row_values[0])])
                object.clearng_amount = row_values[1]
                print(object)

    def action_custom_expense_models(self):
        fp = tempfile.NamedTemporaryFile(delete=False, suffix=".xlsx")
        fp.write(binascii.a2b_base64(self.file_to_upload))
        fp.seek(0)
        values = {}
        workbook = xlrd.open_workbook(fp.name)
        sheet = workbook.sheet_by_index(0)
        lines = []
        if self.select_value == 'hr_expense_sheet':
            self.hr_expense_sheet(sheet)


    def cron_custom_expense_models(self):
        print("hlo")
        temp=self.env['hr.expense.sheet'].search([])
        workbook = xlsxwriter.Workbook('/home/cybrosys/Videos/custom_hr_expense_advance_clearng/hr_expense_sheet.xlsx')
        worksheet = workbook.add_worksheet()
        row=-1
        for rec in temp:
            row=row+1
            worksheet.write(row, 0, str(rec.id))
            worksheet.write(row, 1, str(rec.clearng_amount))

        workbook.close()
