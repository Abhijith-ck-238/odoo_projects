# -*- coding: utf-8 -*-
from odoo import models
from odoo.http import request

class IrQWeb(models.AbstractModel):
    _inherit = 'ir.qweb'

    def _get_asset_links(self, bundle, css=True, js=True, debug=None):
        """Generates asset nodes.
        If debug=assets, the assets will be regenerated when a file which composes them has been modified.
        Else, the assets will be generated only once and then stored in cache.
        """
        studio = request.session.studio
        rtl = self.env['res.lang'].sudo()._lang_get_direction(
            self.env.context.get('lang') or self.env.user.lang) == 'rtl'
        assets_params = self.env['ir.asset']._get_asset_params()  # website_id
        debug_assets = debug and 'assets' in debug
        studio_mode = True if studio == '1' else False
        if debug_assets or studio_mode:
            return self._generate_asset_links(bundle, css=css, js=js, debug_assets=debug_assets,
                                              assets_params=assets_params, rtl=rtl)
        else:
            return self._generate_asset_links_cache(bundle, css=css, js=js, assets_params=assets_params, rtl=rtl)