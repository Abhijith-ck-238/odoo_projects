import time
from odoo import models, fields


class ExcelReportOverdueSales(models.AbstractModel):
    _name = 'report.custom_sales.report_xlsx'
    _inherit = 'report.report_xlsx.abstract'
    _description = 'Report Xlsx Overdue Sales'

    def generate_xlsx_report(self, workbook, data, objs):
        sheet = workbook.add_worksheet('Report')
        head_format = workbook.add_format({
            'align': 'center',
            'bold': True,
            'font_size': '10px',
        })
        data_format = workbook.add_format({
            'font_size': '10px',
        })
        sheet.write(0, 0, '#', head_format)
        sheet.write(0, 1, 'Sale Order', head_format)
        sheet.write(0, 2, 'Reference', head_format)
        sheet.write(0, 3, 'Customer', head_format)
        sheet.write(0, 4, 'Due Date', head_format)
        sheet.write(0, 5, 'Sales Person', head_format)
        sheet.write(0, 6, 'Total', head_format)
        sheet.write(0, 7, 'Amount Due', head_format)
        sheet.write(0, 8, 'Amount Remaining', head_format)

        date_style = workbook.add_format(
            {'text_wrap': True, 'num_format': 'dd/mm/yyyy',
             'font_size': '10px', })

        j = 1
        i = 1
        for invoice in data['data']:
            sheet.write(j, 0, i, data_format)
            i = i + 1
            sheet.write(j, 1, invoice['source_document'], data_format)
            sheet.write(j, 2, invoice['reference'], data_format)
            sheet.write(j, 3, invoice['customer'], data_format)
            sheet.set_column(j, 4, None, date_style)
            sheet.write(j, 4, str(invoice['due_date']), data_format)
            sheet.write(j, 5, invoice['sales_person'], data_format)

            amount_total = invoice['total']
            amount_residual = invoice['amount_due']
            amount_remaining = invoice['remaining']
            currency = invoice['currency']

            # Use string formatting to add commas and currency symbol
            amount_total_with_currency = "{:,.2f} {}".format(amount_total,
                                                             currency.symbol)
            amount_residual_with_currency = "{:,.2f} {}".format(
                amount_residual, currency.symbol)
            amount_remaining_with_currency = "{:,.2f} {}".format(
                amount_remaining, currency.symbol)
            if invoice['is_fi']:
                sheet.write(j, 6, "F.I" + amount_total_with_currency, data_format)
            else:
                sheet.write(j, 6, amount_total_with_currency, data_format)
            sheet.write(j, 7, amount_residual_with_currency, data_format)
            sheet.write(j, 8, amount_remaining_with_currency, data_format)
            j = j + 1

        for total in data['total']:
            j = j+2
            sheet.write(j, 3, 'Due total in ' + total.name + '(' + total.symbol + '):'  , head_format)
            total_due = "{:,.2f} {}".format(
                data['total'][total], total.symbol)
            sheet.write(j, 4, total_due, data_format)

