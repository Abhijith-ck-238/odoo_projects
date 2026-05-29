import json
from odoo import http
from odoo.http import request,content_disposition
from odoo.tools import html_escape

class XLSXReportController(http.Controller):
    @http.route('/offering_xlsx_reports',type='http',auth='user',methods=['POST'],csrf=False)

    def get_report_xlsx(self,model,options,output_format,report_name,**kw):
        uid = request.session.uid
        report_object = request.env[model].with_user(uid)
        options = json.loads(options)
        token = 'dummy-because-api-expects-one'

        try :
            if output_format == "offering_xlsx":
                response = request.make_response(None,headers=[('Content-Type','application/vnd.ms-excel'),('Content-Disposition',content_disposition(report_name + '.xlsx'))])
                report_object.get_xlsx_report(options,response)
            response.set_cookie("fileToken",token)
            return response
        except Exception as e :
            se = http.serialize_exception(e)
            error = {"code":200,"message":"Odoo Server Error","data":se}
        return request.make_response(html_escape(json.dumps(error)))