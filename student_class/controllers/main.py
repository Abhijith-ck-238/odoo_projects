import json
from odoo.http import request, route, Controller

class StudentController(Controller):
    @route("/student_class/standalone_app", auth="public", type="http")
    def standalone_app(self):
        students = request.env['student.class'].sudo().search_read([], ["name", "date", "state", "description"])
        return request.render(
            'student_class.standalone_app',
            {
                'session_info': request.env['ir.http'].get_frontend_session_info(),
                'students': json.dumps(students, default=str),
            }
        )
