import xlrd
from odoo import fields, models
import tempfile
import binascii
from odoo.exceptions import UserError
import xlsxwriter
import json




class ImportCommission(models.Model):
    _name = 'custom.expense.model'

    file_to_upload = fields.Binary('File')
    select_value = fields.Selection([('crossovered_budget','crossovered_budget'),
                                     ('crossovered_budget_lines','crossovered_budget_lines')
                                     ],String="Model")


    def crossovered_budget(self,sheet):
        for row in range(sheet.nrows):
            if row >= 1:
                row_values = sheet.row_values(row)
                print(row_values)
                object = self.env['budget.analytic'].search([('id', '=', row_values[0])])
                object.expense_state = row_values[1]
                object.is_extend_budget_state = row_values[2]
                print(object)

    def crossovered_budget_lines(self,sheet):
        for row in range(sheet.nrows):
            if row >= 1:
                row_values = sheet.row_values(row)
                object = self.env['budget.lines'].search(
                    [('id', '=', row_values[0])])
                object.sudo().write({
                    'amount_to_extend' : float(row_values[1]),

                })


    def action_custom_expense_models(self):
        fp = tempfile.NamedTemporaryFile(delete=False, suffix=".xlsx")
        fp.write(binascii.a2b_base64(self.file_to_upload))
        fp.seek(0)
        values = {}
        workbook = xlrd.open_workbook(fp.name)
        sheet = workbook.sheet_by_index(0)
        lines = []
        if self.select_value == 'crossovered_budget':
            self.crossovered_budget(sheet)
        if self.select_value == 'crossovered_budget_lines':
            self.crossovered_budget_lines(sheet)



    def cron_custom_expense_models(self):
        temp=self.env['budget.analytic'].search([])
        workbook = xlsxwriter.Workbook('/home/cybrosys/Videos/custom_expense/crossovered_budget.xlsx')
        worksheet = workbook.add_worksheet()
        row=-1
        for rec in temp:
            row=row+1
            worksheet.write(row, 0, str(rec.id))
            worksheet.write(row, 1, str(rec.expense_state))
            worksheet.write(row, 2, str(rec.is_extend_budget_state))
        workbook.close()
        temp=self.env['budget.lines'].search([])
        workbook = xlsxwriter.Workbook('/home/cybrosys/Videos/custom_expense/crossovered_budget_lines.xlsx')
        worksheet = workbook.add_worksheet()
        row=-1
        for rec in temp:
               row=row+1
               worksheet.write(row, 0, str(rec.id))
               worksheet.write(row, 1, str(rec.amount_to_extend))
        workbook.close()
