
from odoo import api, fields, models


class OperatingUnit(models.Model):
    _inherit = "operating.unit"

    @api.model
    def _get_edi_invtemplate(self):
        return [('model_id', '=', self.env.ref(
            'account.model_account_invoice').id)]

    invoice_template_id = fields.Many2one('mail.template', 'Invoice Template'
                                          , domain=_get_edi_invtemplate
                                          , help='Set Template to be used as default while sending email')

