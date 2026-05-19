import io
import xlsxwriter
from odoo import models, http, fields
import json
from odoo.tools import  json_default


class project_task(models.Model):
    _inherit = 'offering.config'


    def action_export_template_report_excel(self):
        data = {'record_id': self.id}
        return {
            'type':'ir.actions.report',
            'data': {'model':'offering.config','options':json.dumps(data,default=json_default),
                     'output_format':'offering_xlsx','report_name':'Export Template'},
            'report_type':'offering_xlsx' }



    def get_xlsx_report(self, data,response):
        record_id = data.get('record_id')
        record = self.browse(record_id)

        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})

        sheet = workbook.add_worksheet("Report")
        # setting styles
        # did I go overboard ? probably yes, but it is the only proper way I can think off
        sheet_style_dict = {"align": "center", "text_wrap": True}
        sheet_style = workbook.add_format(sheet_style_dict)

        temaplate_cell_dict = dict({"bg_color": "#EEEEEE"}, **sheet_style_dict)
        template_cell_style = workbook.add_format(temaplate_cell_dict)

        header_style_dict = dict({"bold": True}, **temaplate_cell_dict)
        header_style = workbook.add_format(header_style_dict)

        # changing columns width
        sheet.set_column(3, 9, 22, sheet_style)
        sheet.set_column(0, 3, 17, sheet_style)

        # creating headers
        sheet.write(0, 0, 'External ID', header_style)
        sheet.write(0, 1, 'IQ', header_style)
        sheet.write(0, 2, 'Parent Product', header_style)
        sheet.write(0, 3, 'Product Lines/Temporary Product Name', header_style)
        sheet.write(0, 4, 'Product Lines/Part NO.', header_style)
        sheet.write(0, 5, 'Product Lines/Vendor', header_style)
        sheet.write(0, 6, 'Product Lines/Quantity', header_style)
        sheet.write(0, 7, 'Product Lines/Unit Price', header_style)
        sheet.write(0, 8, 'Product Lines/Policy', header_style)

        index = 1
        for config in record:
            data_id = self.env['ir.model.data'].search([('model', '=', 'offering.config'), ('res_id', '=', config.id)])
            # raise UserError( str(data_id.module) )
            if not data_id:
                data_id = self.env['ir.model.data'].create({
                    'module': '__export__',
                    'name': 'config_' + str(config.id),
                    'model': 'offering.config',
                    'res_id': config.id,
                })

            # creating values
            sheet.write(index, 0, data_id.complete_name, template_cell_style)
            sheet.write(index, 1, config.iq, template_cell_style)
            sheet.write(index, 2, config.product_id.display_name, template_cell_style)
            index += 2
        workbook.close()
        output.seek(0)
        response.stream.write(output.read())
        output.close()

