from odoo import http


class SessionKeepalive(http.Controller):
    @http.route('/session_keepalive', type='json', auth='user')
    def session_keepalive(self):
        return {'timeout': float(http.request.env['ir.config_parameter'].sudo().get_param('session_keepalive.timeout', .25))}
