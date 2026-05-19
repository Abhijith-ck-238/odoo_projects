from odoo.addons.portal.controllers.web import Home
from werkzeug.exceptions import NotFound

from odoo import http
from odoo.exceptions import AccessError
from odoo.http import request, SessionExpiredException


class Website(Home):
    @http.route('/', auth="public", website=True, sitemap=True)
    def index(self, **kw):
        # ✅ Check if user is logged in
        if request.env.user._is_public():
            # User is not logged in → redirect to login page
            return request.redirect('/web/login')

        # Your original homepage logic here
        top_menu = request.website.menu_id
        homepage_url = request.website._get_cached('homepage_url')

        if homepage_url and homepage_url != '/':
            return request.reroute(homepage_url)

        website_page = request.env['ir.http']._serve_page()
        if website_page:
            return website_page

        if homepage_url and homepage_url != '/':
            try:
                rule, args = request.env['ir.http']._match(homepage_url)
                return request._serve_ir_http(rule, args)
            except (AccessError, NotFound, SessionExpiredException):
                pass

        def is_reachable(menu):
            return menu.is_visible and menu.url not in (
                '/', '', '#') and not menu.url.startswith(('/?', '/#', ' '))

        reachable_menus = top_menu.child_id.filtered(is_reachable)
        if reachable_menus:
            return request.redirect(reachable_menus[0].url)

        raise request.not_found()
