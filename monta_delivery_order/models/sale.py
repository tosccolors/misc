# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError
import datetime

class Sale(models.Model):
    _inherit = 'sale.order'

    monta_delivery_block_id = fields.Many2one('monta.delivery.block', 'Monta Delivery Block')

    # @api.onchange('commitment_date')
    # def _check_commitment_date(self):
    #     if self.commitment_date and self.commitment_date.date() <= fields.Datetime.now().date():
    #         raise ValidationError(
    #             _("Delivery date must be future date!")
    #         )

    @api.onchange('expected_date')
    def _onchange_expected_date(self):
        self.commitment_date = self.expected_date
        if not self.commitment_date or (self.commitment_date and self.commitment_date.date() <= fields.Datetime.now().date()):
            self.commitment_date = (fields.Datetime.now() + datetime.timedelta(days=1)).date()

    def action_confirm(self):
        missing_attribute = []
        if self.partner_shipping_id :
            if not self.partner_shipping_id.name:
                missing_attribute.append('Name')
            if not self.partner_shipping_id.street:
                missing_attribute.append('Street')
# TODO: temporarily disabled until street number parsing is fixed
#            if not self.partner_shipping_id.street_number:
#                missing_attribute.append('Street Number')
            if not self.partner_shipping_id.zip:
                missing_attribute.append('Zip')
            if not self.partner_shipping_id.city:
                missing_attribute.append('City')
            if not self.partner_shipping_id.country_id:
                missing_attribute.append('Country')
            if self.partner_shipping_id.country_id and not self.partner_shipping_id.country_id.code:
                missing_attribute.append('Country Code')
            if not self.partner_shipping_id.email:
                missing_attribute.append('Email')
            if not self.partner_shipping_id.phone or not self.partner_shipping_id.mobile:
                missing_attribute.append('Phone/Mobile')

            if missing_attribute:
                raise UserError(_('Please make sure the Delivery Address is correctly set. The following field(s) are missing: "%s". Please update the Delivery Address before confirming the order.', missing_attribute))

        if (self.commitment_date and self.commitment_date.date() <= fields.Datetime.now().date())\
                or not self.commitment_date:
            self.commitment_date = (fields.Datetime.now() + datetime.timedelta(days=1)).date()
            # raise ValidationError(
            #     _("Delivery date must be future date OR cannot be empty!")
            # )
        for self_obj in self:
            if self_obj.website_id:
                continue
            delivery_lines = self_obj.order_line.filtered(lambda l: l.is_delivery)
            if self_obj.carrier_id \
                    and not delivery_lines:
                delivery_lines.unlink()
                carrier_vals = self_obj.carrier_id.rate_shipment(self_obj)
                if carrier_vals.get('success'):
                    delivery_message = carrier_vals.get('warning_message', False)
                    delivery_price = carrier_vals['price']
                    self_obj.set_delivery_line(self_obj.carrier_id, delivery_price)
                    self_obj.write({
                        'recompute_delivery_price': False,
                        'delivery_message': delivery_message,
                    })
        return super().action_confirm()

    @api.onchange('partner_id')
    def _partner_onchange(self):
        carrier = (
                self.with_company(self.company_id).partner_id.property_delivery_carrier_id
                or self.with_company(self.company_id).partner_id.commercial_partner_id.property_delivery_carrier_id
        )
        self.carrier_id = carrier and carrier.id or False
