from odoo.addons.web.controllers import main as web_main
from odoo import http


class Session(web_main.Session):
    @http.route()
    def logout(self, redirect='/web'):
        return super().logout(redirect='/logout')
