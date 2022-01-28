# -*- coding: utf-8 -*-

from odoo import models, fields, api, _

class ResPartnerBank(models.Model):
    _inherit = "res.partner.bank"

    @api.onchange('acc_type', 'acc_number')
    def _popup_acc_type(self):
        result = {}
        if self.acc_number and self.acc_type != 'iban':
            result = {'title': _('Warning'),
                      'message': _('The bank account you have entered is not a valid IBAN. Please check if this is correct')}
        return {'warning': result}