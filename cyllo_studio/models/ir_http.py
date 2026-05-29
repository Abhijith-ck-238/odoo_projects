from odoo import models
from odoo.http import request

class IrHttp(models.AbstractModel):
    _inherit = 'ir.http'

    @classmethod
    def _handle_debug(cls):
        """Override"""
        super()._handle_debug()
        studio = request.httprequest.args.get('studio')
        if studio is not None:
            user = request.env.user.browse(request.session.uid)
            if not user.has_group('base.group_erp_manager'):
                studio = '0'
            request.session.studio = studio if studio == '1' else '0'