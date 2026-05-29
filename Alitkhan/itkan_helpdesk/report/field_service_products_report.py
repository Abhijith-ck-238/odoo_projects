import io
import xlsxwriter
from odoo import models, http, fields
import json
from odoo.tools import  json_default


class project_task(models.Model):
    _inherit = 'project.task'


    def action_product_list_report_excel(self):
        data = {'record_id': self.ids}
        return {
            'type':'ir.actions.report',
            'data': {'model':'project.task','options':json.dumps(data,default=json_default),
                     'output_format':'helpdesk_xlsx','report_name':'Product List Report'},
            'report_type':'helpdesk_xlsx' }


    def get_xlsx_report(self,data,response):
        record_id = data.get('record_id')
        record = self.browse(record_id)

        output = io.BytesIO()

        # Create the workbook and worksheet
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})
        # sheet = workbook.add_worksheet()
        sheet = workbook.add_worksheet("Products")
        # setting styles
        # did I go overboard ? probably yes, but it is the only proper way I can think off
        sheet_style_dict = {"align": "center", "text_wrap": True}
        sheet_style = workbook.add_format(sheet_style_dict)

        temaplate_cell_dict = dict({"bg_color": "#EEEEEE"}, **sheet_style_dict)
        template_cell_style = workbook.add_format(temaplate_cell_dict)

        header_style_dict = dict({"bold": True}, **temaplate_cell_dict)
        header_style = workbook.add_format(header_style_dict)

        # changing columns width
        sheet.set_column(0, 4, 20, sheet_style)

        # creating headers
        sheet.write(0, 0, 'Field Service', header_style)
        sheet.write(0, 1, 'Part No.', header_style)
        sheet.write(0, 2, 'Products', header_style)
        sheet.write(0, 3, 'Requested Quantity', header_style)
        sheet.write(0, 4, 'Available Quantity', header_style)

        TASK_PRODUCT_ID = self.env.ref('itkan_helpdesk.fsm_time_product_1')
        index = 1
        for task in record:
            # creating values
            sheet.write(index, 0, task.name, template_cell_style)
            for order_line in task.sudo().sale_order_id.order_line:
                if order_line.product_id.id == TASK_PRODUCT_ID.id:
                    continue
                else:
                    sheet.write(index, 1, order_line.product_id.default_code)
                    sheet.write(index, 2, order_line.product_id.name)
                    sheet.write(index, 3, order_line.product_uom_qty )
                    sheet.write(index, 4, order_line.product_id.qty_available )
                    index += 1

            index += 2
        workbook.close()
        output.seek(0)
        response.stream.write(output.read())
        output.close()
