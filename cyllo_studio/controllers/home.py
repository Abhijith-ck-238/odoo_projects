from odoo.http import request
from odoo.addons.web.controllers.home import Home
from odoo import http

class ExtendedHome(Home):

    @http.route('/web', type='http', auth="none")
    def web_client(self, s_action=None, **kw):
        studio = request.httprequest.args.get('studio', '0')
        if studio is not None:
            user = request.env.user.browse(request.session.uid)
            if not user.has_group('base.group_erp_manager'):
                studio = '0'
            request.session.studio = studio if studio == '1' else None
        else:
            request.session.studio = None

        return super().web_client(s_action=s_action, **kw)
