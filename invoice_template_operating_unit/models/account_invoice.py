import logging

from odoo import api, fields, models, _

_logger = logging.getLogger(__name__)


class Invoice(models.Model):
    _inherit = 'account.invoice'

    @api.multi
    def action_invoice_sent(self):
        """ Open a window to compose an email, with the edi invoice template
            message loaded by default
            Extended: To Use Template from Operating Unit if set.
        """
        self.ensure_one()

        if self.operating_unit_id and self.operating_unit_id.invoice_template_id:
            template = self.operating_unit_id.invoice_template_id
            custom_layout = "%s.%s" %("invoice_template_operating_unit", self.operating_unit_id.code)

            if not self.env.ref(custom_layout):
                custom_layout = "account.mail_template_data_notification_email_account_invoice"

            _logger.info("template %s \ncustom_layout %s"%(template, custom_layout))

        else:
            template = self.env.ref('account.email_template_edi_invoice', False)
            custom_layout = "account.mail_template_data_notification_email_account_invoice"

        compose_form = self.env.ref('mail.email_compose_message_wizard_form', False)

        ctx = dict(
            default_model='account.invoice',
            default_res_id=self.id,
            default_use_template=bool(template),
            default_template_id=template and template.id or False,
            default_composition_mode='comment',
            mark_invoice_as_sent=True,
            custom_layout=custom_layout,
        )
        return {
            'name': _('Compose Email'),
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'mail.compose.message',
            'views': [(compose_form.id, 'form')],
            'view_id': compose_form.id,
            'target': 'new',
            'context': ctx,
        }
