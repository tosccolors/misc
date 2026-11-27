from odoo import _, models


class ResUsers(models.Model):
    _inherit = 'res.users'

    def _auth_link_generate_action(self, expires=None, redirect=None):
        link = self.env['auth_link.apikeys']._generate_link_for_user(self, expires=expires, redirect=redirect)
        return {
            'type': 'ir.actions.act_window.message',
            'message': self.env['ir.qweb']._render('auth_link.template_key_message', {
                'user': self,
                'link': link,
                'expires': expires,
                'redirect': redirect,
            }),
            'is_html_message': True,
        }
