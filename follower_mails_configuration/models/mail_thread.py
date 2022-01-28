# -*- coding: utf-8 -*-

from odoo import api, models, tools

class MailThread(models.AbstractModel):
    _inherit = 'mail.thread'

    @api.multi
    def message_post_with_template(self, template_id, **kwargs):
        """ Helper method to send a mail with a template
            :param template_id : the id of the template to render to create the body of the message
            :param **kwargs : parameter to create a mail.compose.message woaerd (which inherit from mail.message)
        """
        # Get followers configuration to check whether to disable tracking fields mail or not
        follower_config = self.env['mail.followers.config'].followers_config(self._name, self.ids[0])
        if follower_config and follower_config.stop_track_visibility:
            return self.env['mail.compose.message'].send_mail()

        return super(MailThread, self).message_post_with_template(template_id, **kwargs)