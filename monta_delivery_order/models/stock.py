# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
import json
from odoo.exceptions import UserError

class Picking(models.Model):
    _inherit = 'stock.picking'

    monta_log_id = fields.Many2one('picking.from.odooto.monta', copy=False, string="Monta Log (Create)")
    response_code = fields.Integer(related="monta_log_id.monta_response_code", string='Response Code (Create)')
    response_status = fields.Selection(related="monta_log_id.status", string='Response Status (Create)')
    response_message = fields.Text(related="monta_log_id.monta_response_message", string='Response Message (Create)')
    monta_carrier_tracking_url = fields.Char(string='Monta Tracking URL')


    update_monta_log_id = fields.Many2one('picking.from.odooto.monta', copy=False, string="Monta Log (Update)")
    update_response_code = fields.Integer(related="update_monta_log_id.monta_response_code", string='Response Code (Update)')
    update_response_status = fields.Selection(related="update_monta_log_id.status", string='Response Status (Update)')
    update_response_message = fields.Text(related="update_monta_log_id.monta_response_message", string='Response Message (Update)')

    def transfer_picking_to_monta(self):
        monta_picking_obj = self.env['picking.from.odooto.monta']
        if not (self.sale_id or self.purchase_id) or self.monta_log_id:
            return
        lines = []
        for move in self.move_ids:
            lines.append((0, 0 ,{'move_id':move.id}))

        monta_picking_id = monta_picking_obj.create(
            {'picking_id':self.id, 'status':'draft', 'monta_stock_move_ids': lines})
        self.write({'monta_log_id': monta_picking_id})
        
        if self.picking_type_code == 'outgoing' and self.sale_id:
            monta_picking_id.monta_good_receipt_content()

        if self.picking_type_code == 'incoming' and self.purchase_id:
            monta_picking_id.monta_inbound_forecast_content()
        return monta_picking_id

    def update_picking_to_monta(self):
        """
        Update Call to Monta, usually for change in Planned Date
        """
        monta_picking_obj = self.env['picking.from.odooto.monta']
        if not (self.sale_id or self.purchase_id) or not self.monta_log_id:
            return

        if self.state in ('done', 'cancel'):
            return

        monta_picking_id = monta_picking_obj.create(
            {'picking_id': self.id, 'status': 'draft', 'method_type': 'update'})

        self.write({'update_monta_log_id': monta_picking_id})

        # TODO: If Outbound update required in future:
        # if self.picking_type_code == 'outgoing' and self.sale_id:
        #     monta_picking_id.monta_good_receipt_content()

        if self.picking_type_code == 'incoming' and self.purchase_id:
            monta_picking_id.monta_inbound_forecast_update_content()
        return monta_picking_id

    def button_validate(self):
        res = super().button_validate()
        if self.picking_type_code in ('outgoing', 'incoming') and (self.sale_id or self.purchase_id) and not self.monta_log_id and self.state not in ('draft','done', 'cancel'):
            self.transfer_picking_to_monta()
        return res

    def action_assign(self):
        res = super().action_assign()
        if self.picking_type_code in ('outgoing', 'incoming') and (self.sale_id or self.purchase_id) and not self.monta_log_id and self.state not in (
        'draft', 'done', 'cancel'):
            self.transfer_picking_to_monta()
        return res

    def action_confirm(self):
        res = super().action_confirm()
        if self.picking_type_code in ('outgoing', 'incoming') and (self.sale_id or self.purchase_id) and not self.monta_log_id:
            self.transfer_picking_to_monta()
        return res

    def open_website_url(self):
        self.ensure_one()
        if not self.monta_carrier_tracking_url:
            raise UserError(_("Your delivery method has no redirect on courier provider's website to track this order."))

        carrier_trackers = []
        try:
            carrier_trackers = json.loads(self.monta_carrier_tracking_url)
        except ValueError:
            carrier_trackers = self.monta_carrier_tracking_url
        else:
            msg = "Tracking links for shipment: <br/>"
            for tracker in carrier_trackers:
                msg += '<a href=' + tracker[1] + '>' + tracker[0] + '</a><br/>'
            self.message_post(body=msg)
            return self.env["ir.actions.actions"]._for_xml_id("delivery.act_delivery_trackers_url")

        client_action = {
            'type': 'ir.actions.act_url',
            'name': "Shipment Tracking Page",
            'target': 'new',
            'url': self.monta_carrier_tracking_url,
        }
        return client_action

    def post_admin_notification(self, msg='', type=''):
        #force admin id =2, else sudo will gives odoo bot
        admin_user = self.env['res.users'].sudo().browse(2)
        partner = admin_user.partner_id
        
        subject = "Error: Monta %s scheduler for %s" %(type, self.name)
        message_obj = self.message_post(body=msg, subject=subject, message_type="notification",
                                       subtype_xmlid="mail.mt_comment", partner_ids=partner.ids,
                                       author_id=partner.id, notify_by_email=False)

        message_obj.notification_ids = [(0, 0, {'mail_message_id': message_obj.id, 'res_partner_id': partner.id,
                                                'notification_type': 'inbox'})]

        return


    def action_send2monta_interface(self):
        """ Call Update to Monta"""

        if self.state in ('done', 'cancel'):
            return

        # Call Create:
        if not self.monta_log_id or self.monta_log_id.monta_response_code != 200:
            return self.transfer_picking_to_monta()

        # Call Update:
        if self.monta_log_id:
            return self.update_picking_to_monta()


    def write(self, vals):
        res = super().write(vals)
        for record in self:
            # Call to update Monta
            if 'scheduled_date' in vals:
                record.update_picking_to_monta()
        return res



class MoveLine(models.Model):
    _inherit = 'stock.move.line'

    monta_batch_ref = fields.Char('Monta Batch Ref')



