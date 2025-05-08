from odoo import api, fields, models, _
import requests
from requests.auth import HTTPBasicAuth
from odoo.exceptions import AccessError
import json
import logging
from datetime import datetime
import pytz
from pytz import timezone
from odoo.tools import  DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT


_logger = logging.getLogger(__name__)


class PickingfromOdootoMonta(models.Model):
    _name = 'picking.from.odooto.monta'
    _inherit = ['mail.thread']
    _order = 'create_date desc'
    _rec_name = 'picking_id'
    _description = 'Picking Odoo To Monta'

    @api.depends('monta_response_code')
    def _compute_response(self):
        for pick in self:
            pick.status = 'draft'
            if pick.monta_response_code == 200:
                pick.picking_monta_response = True
                pick.status = 'successful'
            elif pick.monta_response_code and pick.monta_response_code != 200:
                pick.picking_monta_response = False
                pick.status = 'failed'

    @api.depends('picking_id.move_line_ids', 'picking_id.move_ids')
    def _compute_batch_status(self):
        for pick in self:
            batch_status = 'no_batches'
            batches_obj = pick.monta_stock_move_ids.mapped('monta_outbound_batch_ids')
            inbound_obj = pick.monta_stock_move_ids.mapped('monta_inbound_line_ids')
            if not inbound_obj and not batches_obj:
                pick.batches_status = batch_status
                continue
            for stock_move in pick.picking_id.move_ids:
                total_qty_done = sum(stock_move.move_line_ids.mapped('qty_done'))
                if stock_move.move_line_ids \
                        and stock_move.move_line_ids.filtered(lambda ml: ml.lot_name or ml.lot_id) \
                        and stock_move.product_uom_qty != total_qty_done:
                    batch_status = 'partial_received'
            if pick.picking_id.move_line_ids \
                    and pick.picking_id.move_line_ids.filtered(lambda ml: ml.lot_name or ml.lot_id):
                if batch_status == 'no_batches':
                    batch_status = 'received'
            pick.batches_status = batch_status
                
    @api.depends('picking_id')
    def _compute_order_name(self):
        for pick in self:
            name = ''
            name += pick.picking_id.name.replace('/', '')
            if pick.sale_id:
                name = pick.sale_id.name +' ' + name
            if pick.purchase_id:
                name = pick.purchase_id.name +' ' + name
            pick.monta_order_name = name

    picking_id = fields.Many2one('stock.picking', required=True)
    picking_type_code = fields.Selection(related='picking_id.picking_type_code')
    sale_id = fields.Many2one('sale.order', related="picking_id.sale_id")
    purchase_id = fields.Many2one('purchase.order', related="picking_id.purchase_id")
    partner_delivery_address_id = fields.Many2one('res.partner',related="picking_id.partner_id")
    partner_invoice_address_id = fields.Many2one('res.partner', related="sale_id.partner_invoice_id", string='Invoice Address')
    shipping_comment = fields.Html(related="picking_id.note",string='Shipping Comment')
    planned_shipment_date = fields.Datetime(related="picking_id.scheduled_date",string='Planned Shipment Date/Ship On Planned Shipment Date/Delivery Date Requested')
    shipped = fields.Datetime(related="picking_id.date_done",string= 'Shipped') #picking.Shipped date done
    monta_stock_move_ids = fields.One2many('stock.move.from.odooto.monta', 'monta_move_id')
    monta_response_code = fields.Integer('Monta Response')
    monta_response_message = fields.Text('Monta Response Message')
    picking_monta_response = fields.Boolean(compute=_compute_response, default=False, store=True, string='Monta Response')
    json_payload = fields.Text('Payload')
    client_order_ref = fields.Char(string="Customer Reference", related="picking_id.client_order_ref")
    status = fields.Selection([('draft', 'Not yet sent to Monta'), ('successful', 'Successfully sent to Monta'), ('failed', 'Not successfully sent to Monta')], string='Status',
                              required=True, readonly=True, store=True, compute=_compute_response)
    monta_order_name = fields.Char(string="Monta Order Name", compute=_compute_order_name, store=True)
    message = fields.Char('Error/Exception Message')
    picking_status = fields.Selection(related="picking_id.state", string="Picking Status", store=True)
    batches_status = fields.Selection([('no_batches', 'No Batches Received'), ('received', 'Batches Received'),
                              ('partial_received', 'Partial Batches Received')], string='Batch Status', readonly=True, store=True, compute=_compute_batch_status)

    method_type = fields.Selection([('create', 'CREATE'), ('update', 'Update')], help="API method type"
                                   , string='API Method', default='create', copy=False)

    def write_response(self, message=None):
        if message is None:
            return
        self.message_post(body=message)

    def call_monta_interface(self, request, method):
        config = self.env['monta.config'].search([], limit=1)
        payload = self.json_payload
        headers = {
            'Content-Type': 'application/json'
        }

        url = config.host

        if url.endswith("/"):
            url += method
        else:
            url += '/'+method
        user = config.username
        pwd = config.password
        response = False
        try:
            response = requests.request(request, url, headers=headers, data=payload, auth=HTTPBasicAuth(user, pwd))
            if response.status_code == 200 and 'GET' in method:
                return response

            dic ={
                'monta_response_code': response.status_code,
                'monta_response_message': response.text,
            }
            if response.status_code == 200 and method == 'inboundforecast/group':
                monta_lines = []
                response_data = json.loads(response.text)
                for line in self.monta_stock_move_ids:
                    line_dt = next((item for item in response_data['InboundForecasts'] if item["Sku"] == line.product_id.default_code), None)
                    if line_dt:
                        monta_lines.append((1, line.id, {'monta_inbound_forecast_id':line_dt['InboundForecastId']}))
                dic['monta_stock_move_ids'] = monta_lines
                # self.message_post(body=_("Original Response ===> %s" % (response)))
                # self.message_post(body=_("JSON Response ===> %s" % (response_data)))
            self.write(dic)
        except Exception as e:
            raise AccessError(
                _('Error Monta Interface call: %s') % (e))
        return response

    def update_monta_interface(self, request, method):
        config = self.env['monta.config'].search([], limit=1)

        payload = self.json_payload
        headers = {
            'Content-Type': 'application/json'
        }

        url = config.host

        if url.endswith("/"):
            url += method + '/' + self.monta_order_name
        else:
            url += '/' + method + '/' + self.monta_order_name
        user = config.username
        pwd = config.password
        response = False
        try:
            response = requests.request(request, url, headers=headers, data=payload, auth=HTTPBasicAuth(user, pwd))
            if response.status_code == 200 and 'GET' in method:
                return response

            dic = {
                'monta_response_code': response.status_code,
                'monta_response_message': response.text,
            }
            self.write(dic)
        except Exception as e:
            raise AccessError(
                _('Error Monta Interface call: %s') % (e))
        return response

    def monta_good_receipt_content(self, button_action=False):
        config = self.env['monta.config'].search([], limit=1)
        acc_tax = self.env['account.tax']
        planned_shipment_date = self.planned_shipment_date.isoformat()
        shipped = self.shipped.isoformat() if self.shipped else planned_shipment_date
        delivery_add = self.partner_delivery_address_id
        invoice_add  = self.partner_invoice_address_id if self.sale_id else self.partner_delivery_address_id
        blocked = False
        blocked_msg = ''
        if self.sale_id and self.sale_id.monta_delivery_block_id:
            blocked = True
            blocked_msg = self.sale_id.monta_delivery_block_id.name

        payload = {
            "WebshopOrderId": self.monta_order_name,
            "Reference": self.client_order_ref or '',
            "Origin": config.origin,
            "orderCreate": '',
            "ConsumerDetails":{
                "DeliveryAddress": {
                        "Company": delivery_add.name,
                        "FirstName": delivery_add.firstname or '',
                        "MiddleName": '',
                        "LastName": delivery_add.lastname,
                        "Street": (delivery_add.street_name if delivery_add.street_name else ' ')+' '+(delivery_add.street2 if delivery_add.street2 else ' '),
                        "HouseNumber": (delivery_add.street_number if delivery_add.street_number else ' ') + '-'+ (delivery_add.street_number2 if delivery_add.street_number2 else ' '),
                        "HouseNumberAddition": '',
                        "PostalCode": delivery_add.zip,
                        "City": delivery_add.city,
                        "State": delivery_add.state_id.code or '',
                        "CountryCode": delivery_add.country_id.code,
                        "PhoneNumber": delivery_add.mobile or '',
                        "EmailAddress": delivery_add.email
                },
                "InvoiceAddress": {
                    "Company": invoice_add.name,
                    "FirstName": invoice_add.firstname or '',
                    "MiddleName": '',
                    "LastName": invoice_add.lastname,
                    "Street":   (invoice_add.street_name if invoice_add.street_name else ' ')+' '+(invoice_add.street2 if invoice_add.street2 else ' '),
                    "HouseNumber": (invoice_add.street_number if invoice_add.street_number else ' ') + '-'+ (invoice_add.street_number2 if invoice_add.street_number2 else ' '),
                    "HouseNumberAddition": '',
                    "PostalCode": invoice_add.zip,
                    "City": invoice_add.city,
                    "State": invoice_add.state_id.code or '',
                    "CountryCode": invoice_add.country_id.code,
                    "PhoneNumber": invoice_add.mobile or '',
                    "EmailAddress": invoice_add.email
                },
                "InvoiceDebtorNumber": '',
                "B2B": True,
                "ShippingComment": self.shipping_comment or ''
            },
            "PlannedShipmentDate": planned_shipment_date,
            "ShipOnPlannedShipmentDate": True if planned_shipment_date else False,
            "Blocked": blocked,
            "BlockedMessage": blocked_msg,
            "Quarantaine": '',
            "DeliveryDateRequested": planned_shipment_date,
            "Lines":[],
            "Picking": True,
            "Picked": '',
            "AllowedShippers":[],
            "Shipped": shipped,
            "PackingServiceText": '',
            "Family": '',
            "Comment":self.client_order_ref or '',
            "PickbonIds": ''
        }

        for line in self.monta_stock_move_ids:
            payload['Lines'].append({
                "Sku": line.product_id.default_code,
                "OrderedQuantity": int(line.ordered_quantity)
            })

        sale_obj = self.sale_id
        if sale_obj.carrier_id:
            delivery_method = self.sale_id.carrier_id
            payload['AllowedShippers'].append(
                delivery_method.monta_shipper_code
            )

        payload['Invoice'] = {
            "PaymentMethodDescription": "",
            "AmountInclTax":sale_obj.amount_total,
            "TotalTax": sale_obj.amount_tax,
            "Paid": False,
            "WebshopFactuurID": sale_obj.name[1:],
            "Currency": sale_obj.currency_id.name,
            "Lines":[],
        }
        invoice_lines = []
        for sol in sale_obj.order_line:
            tax_obj = sol.tax_id[0] if sol.tax_id else self.env['account.tax']
            sol_item = {
                "Quantity": int(sol.product_uom_qty),
                "TaxPercentage": tax_obj.amount,
                "TaxAmount": sol.price_tax,
                "TaxDescription": tax_obj.name,
                "AmountInclTax": sol.price_total,
                "AmountExclTax": sol.price_subtotal,
                "Discount": False,
                "PaymentCosts": False,
                "ShippingCost": False,
                "Description": sol.name,
            }

            if sol.product_id.type == 'service':
                #discount line
                if sol.price_total < 0:
                    sol_item.update({
                        "Discount": True,
                   })
                #shipping line
                elif sol.product_id.id == sale_obj.carrier_id.product_id.id:
                    sol_item.update({
                        "ShippingCost": True,
                    })
            else:
                sol_item_convert_tax = acc_tax._convert_to_tax_base_line_dict(
                    self,
                    partner=sol.order_id.partner_id,
                    currency=sol.order_id.currency_id,
                    product=sol.product_id,
                    taxes=sol.tax_id,
                    price_unit=sol.price_unit,
                    quantity=1,
                    discount=sol.discount,
                    price_subtotal=sol.price_subtotal,
                )
                item_tax_results = acc_tax._compute_taxes([sol_item_convert_tax])
                item_totals = list(item_tax_results['totals'].values())[0]
                item_amount_untaxed = item_totals['amount_untaxed']
                item_amount_tax = item_totals['amount_tax']
                item_amount_incl_tax = item_amount_untaxed + item_amount_tax
                sol_item.update({
                    "ItemPriceInclTax": item_amount_incl_tax,
                    "ItemPriceExclTax": sol.price_unit,
                    "Sku": sol.product_id.default_code,
                    "Reference": sol.product_id.name
                })

            invoice_lines.append(sol_item)
        payload['Invoice']['Lines'] = invoice_lines
        payload = json.dumps(payload)
        self.write({"json_payload": payload})
        if not button_action:
            self.call_monta_interface("POST", "order")

    def monta_inbound_forecast_content(self, button_action=False):
        planned_shipment_date = self.planned_shipment_date.isoformat()
        payload = {
                "Reference": self.monta_order_name,
                "InboundForecasts":[],
                "DeliveryDate": planned_shipment_date
            }
        for line in self.monta_stock_move_ids:
            payload['InboundForecasts'].append({
                "DeliveryDate": planned_shipment_date,
                "Sku": line.product_id.default_code,
                "Quantity": str(int(line.ordered_quantity))
            })
        payload = json.dumps(payload)
        self.write({"json_payload": payload})
        if not button_action:
            response = self.call_monta_interface("POST", "inboundforecast/group")
            return response


    def monta_inbound_forecast_update_content(self, button_action=False):
        "Update content, for now it would be for Planned Shipment"
        planned_shipment_date = self.planned_shipment_date.isoformat()
        payload = {
                "ExpectedDeliveryDate": planned_shipment_date
            }
        payload = json.dumps(payload)
        self.write({"json_payload": payload})
        response = self.update_monta_interface("PUT", "inboundforecast/group")
        return response

    # def generate_payload(self):
    #     if self.mothod_type == 'create':
    #         if self.picking_type_code == 'outgoing' and self.sale_id:
    #             self.monta_good_receipt_content(True)
    #         elif self.picking_type_code == 'incoming' and self.purchase_id:
    #             self.monta_inbound_forecast_content(True)

    def action_call_monta_interface(self):
        # FIXME: Not needed, commented in the view
        if self.picking_type_code == 'outgoing' and self.sale_id:
            self.call_monta_interface("POST", "order")
        elif self.picking_type_code == 'incoming' and self.purchase_id:
            self.call_monta_interface("POST", "inboundforecast/group")

    # def action_update_monta_interface(self):
    #     # TODO: If Outbound update required in future:
    #     # if self.picking_type_code == 'outgoing' and self.sale_id:
    #     #     self.update_monta_interface("PUT", "order")
    #     if self.picking_type_code == 'incoming' and self.purchase_id:
    #         self.update_monta_interface("PUT", "inboundforecast/group")

    def convert_TZ_UTC(self, TZ_datetime):
        shipped_date = datetime.strptime(TZ_datetime, '%Y-%m-%dT%H:%M:%S.%f').strftime('%Y-%m-%d %H:%M:%S')
        shipped_date = datetime.strptime(shipped_date, '%Y-%m-%d %H:%M:%S')
        tz_name = self.env.context.get('tz') or self.env.user.tz
        if not tz_name:
            _logger.info(
                "\nError: Monta scheduler! Timezone missing for user %s(Id=%s)!\n," % (self.env.user.name, self.env.user.id)
            )
        user_tz = pytz.timezone(tz_name)
        utc = pytz.utc
        dt = user_tz.localize(shipped_date).astimezone(utc).strftime('%Y-%m-%d %H:%M:%S')
        return dt

    @api.model
    def _cron_monta_get_outbound_batches(self):
        method = "order/%s/batches"
        monta_move_obj = odoo_outbound_lines_obj = self.env['stock.move.from.odooto.monta']
        monta_outbond_obj = self.env['monta.stock.lot']
        prod_obj = self.env['product.product']
        emailTemplate = self.env.ref("monta_delivery_order.email_template_notify_monta_exception", raise_if_not_found=False)


        for obj in self.search([('picking_id.picking_type_code', '=', 'outgoing'),
                                ('picking_id.state', 'not in', ('draft', 'done', 'cancel')), ('status', '=', 'successful')]):
            try:
                orderNum = obj.monta_order_name
                response = self.call_monta_interface("GET", method%orderNum)
                response_order_info = self.call_monta_interface("GET", "order/%s"%orderNum)
                track_dic = {}
                if response.status_code == 200:
                    response_data = json.loads(response.text)
                    message = 'Outbound Schedular Batches Response: ' + json.dumps(response_data)

                    monta_delivery_block_id = obj.picking_id.sale_id.monta_delivery_block_id
                    shipped_date = False
                    if response_order_info.status_code == 200 \
                            and (not monta_delivery_block_id or (monta_delivery_block_id and not monta_delivery_block_id.no_tracking)):

                        response_order_info_data = json.loads(response_order_info.text)
                        message += '<br/>Outbound Schedular Tracking Response: ' + json.dumps(response_order_info_data)

                        shipped_date = response_order_info_data['Shipped']
                        shipped_date = self.convert_TZ_UTC(shipped_date) if shipped_date else shipped_date
                        if obj.picking_id.sale_id:
                            if not obj.picking_id.carrier_tracking_ref \
                                or (obj.picking_id.carrier_tracking_ref != response_order_info_data['TrackAndTraceCode']):
                                track_dic['Shipped'] = response_order_info_data['Shipped']
                                track_dic['TrackAndTraceLink'] = response_order_info_data['TrackAndTraceLink']
                                track_dic['TrackAndTraceCode'] = response_order_info_data['TrackAndTraceCode']
                                track_dic['ShipperDescription'] = response_order_info_data['ShipperDescription']
                                track_dic['PackingServices'] = response_order_info_data['PackingServices']


                    for line in response_data.get('BatchLines', []):
                        sku = line['Sku']
                        batch_content = line['BatchContent']
                        qty = abs(int(line['Quantity']))
                        odoo_outbound_line = monta_move_obj.search(
                            [('product_id.default_code', '=', sku), ('monta_move_id.monta_order_name', '=', obj.monta_order_name)])
                        if odoo_outbound_line:
                            odoo_outbound_lines_obj |= odoo_outbound_line

                            batch_ref = batch_id = ''

                            # tracking products
                            if batch_content:
                                batch_ref = batch_content['Title']
                                batch_id = batch_content['Id']

                                batch_qty_total = 0
                                batch_ids = odoo_outbound_line.monta_outbound_batch_ids
                                batch_obj = odoo_outbound_line.monta_outbound_batch_ids.\
                                    search([('id', 'in', batch_ids.ids),
                                            ('batch_id', '=', batch_id),
                                            ('batch_ref', '=', batch_ref)])
                                if batch_obj:
                                    batch_qty_total = sum(batch_obj.mapped('batch_quantity'))

                                if batch_qty_total >= odoo_outbound_line.ordered_quantity:
                                    continue

                                data = {'batch_id':batch_id,
                                        'batch_ref':batch_ref,
                                        'batch_quantity':qty,
                                        'monta_outbound_id': odoo_outbound_line.id}

                                if shipped_date:
                                    data.update({'monta_create_date': shipped_date})
                                # batch created
                                monta_outbond_obj.create(data)

                            # Non tracking products:
                            elif not batch_ref:
                                if odoo_outbound_line.product_tracking == 'none':
                                    odoo_outbound_line.done_quantity = qty
                                    if shipped_date:
                                        odoo_outbound_line.monta_shipped_date = shipped_date
                                else:
                                    # Notify Salesperson:
                                    emailTemplate.send_mail(obj.id, force_send=True)
                                    continue

                                if qty > odoo_outbound_line.ordered_quantity:
                                    continue

                    obj.write_response(message)

                if obj.picking_id.sale_id and track_dic:
                    body = _('Tracking Info:\n %s', track_dic['TrackAndTraceLink'])
                    obj.picking_id.sale_id.message_post(body=body)
                    obj.picking_id.\
                        write({'monta_carrier_tracking_url':track_dic['TrackAndTraceLink'],
                               'carrier_tracking_ref':track_dic['TrackAndTraceCode']})
            except Exception as e:
                error_message = "\nError: Monta Outbound scheduler %s\n,"%(e)
                _logger.info(
                    error_message
                )
                # obj.picking_id.post_admin_notification(error_message, 'Outbound')
                obj.picking_id.message_post(body=_("%s" % (error_message)))
        if odoo_outbound_lines_obj:
            self.env['monta.inboundto.odoo.move'].validate_picking_from_monta_qty(outboundMoveData=odoo_outbound_lines_obj)


class PickingLinefromOdootoMonta(models.Model):
    _name = 'stock.move.from.odooto.monta'
    _order = 'create_date desc'
    _rec_name = 'monta_move_id'
    _description = 'Move Odoo To Monta'

    move_id = fields.Many2one('stock.move', required=True)
    monta_move_id = fields.Many2one('picking.from.odooto.monta', required=True)
    product_id = fields.Many2one('product.product', related='move_id.product_id')
    ordered_quantity = fields.Float(related='move_id.product_qty', string='Ordered Quantity')
    done_quantity = fields.Float(string='Done Quantity', help="Shipped Qty, captured for Non Tracking SKU")
    monta_shipped_date = fields.Datetime(string="Monta Shipped Date", help="Monta Shipped date, captured for Non Tracking SKU")
    product_tracking = fields.Selection(related='move_id.product_id.tracking', store=True)
    monta_inbound_forecast_id = fields.Char("Monta Inbound Forecast Id")
    monta_inbound_line_ids = fields.One2many('monta.inboundto.odoo.move', 'monta_move_line_id')
    monta_outbound_batch_ids = fields.One2many('monta.stock.lot', 'monta_outbound_id')


class MontaInboundtoOdooMove(models.Model):
    _name = 'monta.inboundto.odoo.move'
    _order = 'create_date desc'
    _rec_name = 'monta_move_line_id'
    _description = 'Monta Inbound'

    monta_move_line_id = fields.Many2one('stock.move.from.odooto.monta', required=True)
    inbound_id = fields.Char('Inbound ID')
    product_id = fields.Many2one('product.product', related='monta_move_line_id.product_id')
    inbound_quantity = fields.Float(string='Inbound Quantity')
    monta_batch_ids = fields.One2many('monta.stock.lot', 'monta_inbound_id')

    def apply_backdate(self, pickObj):
        date = False
        if pickObj.picking_type_code == 'outgoing':

            allDates = []
            moves = pickObj.monta_log_id.monta_stock_move_ids

            # Batched SKUs: Shipped dates
            if moves.monta_outbound_batch_ids.mapped('monta_create_date'):
                allDates += moves.monta_outbound_batch_ids.mapped('monta_create_date')

            # Non Tracking SKUs: Shipped dates
            if moves.mapped('monta_shipped_date'):
                allDates += moves.mapped('monta_shipped_date')

            date = max(allDates, default=None)

        elif pickObj.picking_type_code == 'incoming':
            # date = max(pickObj.monta_log_id.monta_stock_move_ids.
            #            monta_inbound_line_ids.monta_batch_ids.mapped('monta_create_date')
            #          , default=None)

            allDates = []
            moves = pickObj.monta_log_id.monta_stock_move_ids

            # Batched SKUs: Shipped dates
            if moves.monta_outbound_batch_ids.mapped('monta_create_date'):
                allDates += moves.monta_inbound_line_ids.mapped('monta_create_date')

            # Non Tracking SKUs: Shipped dates
            if moves.mapped('monta_shipped_date'):
                allDates += moves.mapped('monta_shipped_date')

            date = max(allDates, default=None)

        if date:
            pickObj.move_line_ids.write(
                {
                    "date_backdating": date,
                }
            )
        return

    def partial_validation_from_monta(self, pickObj, ctx):
        #Mostly called for incoming partial shipment
        backorderConfirmObj = self.env['stock.backorder.confirmation']

        approved = []
        if pickObj.picking_type_code == 'incoming':
            method = "inboundforecast/group/"+pickObj.monta_log_id.monta_order_name
            response = self.env['picking.from.odooto.monta'].call_monta_interface("GET", method)
            if response.status_code == 200:
                response_data = json.loads(response.text)
                message = "Inbound Schedular 'API inboundforecast/group' Response " + json.dumps(response_data)
                # pickObj.monta_log_id.write_response(message)
                pickObj.message_post(body=message)
                approved = [val['Approved'] for i, val in enumerate(response_data['InboundForecasts']) if not val['Approved']]
            else:
                message = "Inbound Schedular 'API inboundforecast/group' Response "+ str(response.status_code)
                # return pickObj.monta_log_id.write_response(message)
                return pickObj.message_post(body=message)

        if len(approved) == 0:
            res = pickObj.with_context(ctx).button_validate()
            if res is True:
                return res
            ctx = res['context']
            # cancel backorder and validate picking
            line_fields = [f for f in backorderConfirmObj._fields.keys()]
            backOrderData = backorderConfirmObj.with_context(ctx).default_get(line_fields)
            backOrderId = backorderConfirmObj.with_context(ctx).create(backOrderData)
            backOrderId.with_context(
                ctx).process_cancel_backorder() # partial force validation create new line with 0 qty done

        return True

    def validate_picking_from_monta_qty(self, inboundMoveData={}, outboundMoveData={}):
        ctx = self.env.context.copy()
        #Imp: Add all parameter to skip _pre_action_done_hook()
        ctx.update({
            'skip_immediate':True,
            'skip_sms':True,
            'skip_expired':True})
        picking_obj = self.env['stock.picking']
        update_picking_msg = {}
        monta_obj = self.env['picking.from.odooto.monta']

        def _assign_lot(moveObj, lotRef, qty):
            try:
                product = moveObj.product_id
                picking = moveObj.picking_id

                data = {'picking_id': picking.id,
                        'product_id': product.id,
                        'qty_done': qty}

                if picking.picking_type_code == 'incoming':
                    data.update({'lot_name': lotRef})
                elif picking.picking_type_code == 'outgoing':
                    lot = self.env['stock.lot'].search(
                        [('name', '=', lotRef),('product_id', '=', product.id),
                         ('company_id', '=', moveObj.company_id.id)])
                    if not lot:
                        lot = lot.create({'name':lotRef,
                                    'product_id':product.id,
                                    'company_id':moveObj.company_id.id})
                    if lot:
                        data.update({'lot_id': lot.id})

                if ('lot_name' in data) or ('lot_id' in data):
                    movelineObj = moveObj.move_line_ids

                    # Update "Done Qty" - found matched Lot Moveline
                    if ('lot_id' in data):
                        mln = moveObj.move_line_ids.filtered(lambda x: x.lot_id.id == data['lot_id'])
                        mln.qty_done = qty
                    else:
                        mln = moveObj.move_line_ids.filtered(lambda x: x.lot_id.name == data['lot_name'])
                        mln.qty_done = qty

                    # If Moveline not found, create New Line.
                    if not mln.id:
                        moveObj.write({'move_line_ids': [(0, 0, data)]})
                        mln = moveObj.move_line_ids-movelineObj

                    # moveObj.write({'move_line_ids': [(0, 0, data)]})
                    # return moveObj.move_line_ids-movelineObj
                    return mln
            except Exception as e:
                _logger.info(
                    "\nError: Monta Assigning LOT %s,\n" % (e)
                )
                return []

        # GET inbound
        for odoo_inbound_line in inboundMoveData:
            moveObj = odoo_inbound_line.move_id
            monta_log_id = moveObj.picking_id.monta_log_id
            msg = ''
            if moveObj.state in ('confirmed', 'partially_available', 'assigned'):
                picking_obj |= moveObj.picking_id

                for batch_obj in odoo_inbound_line.monta_inbound_line_ids.mapped('monta_batch_ids'):
                    if batch_obj.stock_move_line:
                        continue
                    batch_quantity = batch_obj.monta_inbound_id.inbound_quantity
                    try:
                        new_move_line = _assign_lot(moveObj, batch_obj.batch_ref, batch_quantity)
                        if new_move_line:
                            batch_obj.stock_move_line = new_move_line
                    except Exception as e:
                        msg += "Error: Inbound lot/serial number assigning: %s''!!\n" % (e)

                # Non tracking products:
                if not odoo_inbound_line.monta_outbound_batch_ids:
                    product = moveObj.product_id
                    inline = odoo_inbound_line.monta_inbound_line_ids.filtered(lambda x: x.product_id.id == product.id)
                    odoo_inbound_line.done_quantity = inline and inline.inbound_quantity or 0
                    if product.product_tmpl_id.tracking == 'none':
                        mln = moveObj.move_line_ids.filtered(lambda x: x.product_id.id == product.id)
                        mln.qty_done = odoo_inbound_line.done_quantity

                update_picking_msg[monta_log_id] = msg

            monta_obj |= monta_log_id

        # GET Outbound
        for odoo_outbound_line in outboundMoveData:
            moveObj = odoo_outbound_line.move_id
            monta_log_id = moveObj.picking_id.monta_log_id
            msg =''
            if moveObj.state in ('confirmed', 'partially_available', 'assigned'):
                picking_obj |= moveObj.picking_id
                for batch_obj in odoo_outbound_line.monta_outbound_batch_ids:
                    if batch_obj.stock_move_line:
                        continue
                    try:
                        new_move_line = _assign_lot(moveObj, batch_obj.batch_ref, batch_obj.batch_quantity)
                        if new_move_line:
                            batch_obj.stock_move_line = new_move_line
                    except Exception as e:
                        msg += "Error: Outbound lot/serial number assigning: %s''!!\n" % (e)

                # Non tracking products:
                if not odoo_outbound_line.monta_outbound_batch_ids:
                    product = moveObj.product_id
                    if product.product_tmpl_id.tracking == 'none':
                        mln = moveObj.move_line_ids.filtered(lambda x: x.product_id.id == product.id)
                        mln.qty_done = odoo_outbound_line.done_quantity

                update_picking_msg[monta_log_id] = msg
                monta_obj |= monta_log_id

        for pickObj in picking_obj:
            monta_obj |= pickObj.monta_log_id
            try:
                if pickObj.monta_log_id not in update_picking_msg:
                    update_picking_msg[pickObj.monta_log_id] = ''
                # ctx.update({'picking_ids_not_to_backorder':pickObj.ids})

                #apply backdate, if monta_create_date
                self.apply_backdate(pickObj)

                if pickObj.picking_type_code == 'incoming':
                    self.partial_validation_from_monta(pickObj, ctx)
                else:
                    # ctx.update({'picking_ids_not_to_backorder':pickObj.ids})
                    pickObj.with_context(ctx).button_validate()
                    
                # _logger.info(
                #     "\nWarning: Monta Outbound/Inbound scheduler after "
                #     "button_validate() proceeded with partial validation %s,\n" % (res)
                # )
                # self.partial_validation_from_monta(pickObj, res)

            except Exception as e:
                pickObj |= pickObj
                msg = ("Error Validating Picking: %s''!!\n" % (e))
                update_picking_msg[pickObj.monta_log_id] = msg

        for monta_obj, message in update_picking_msg.items():
            monta_obj.write({'message':message})


    @api.model
    def _cron_monta_get_inbound(self):
        odoo_inbound_lines_obj = self.env['stock.move.from.odooto.monta']
        method = 'inbounds'
        config = self.env['monta.config'].search([], limit=1)
        if config.inbound_id:
            method = "inbounds?sinceid=" + config.inbound_id
        response = self.env['picking.from.odooto.monta'].call_monta_interface("GET", method)
        if response.status_code == 200:
            monta_inbound_ids = []
            response_data = json.loads(response.text)

            for dt in response_data:
                picking_obj = self.env['stock.picking']
                try:
                    inboundID = dt['Id']
                    monta_inbound_ids.append(int(inboundID))
                    sku = dt['Sku']
                    inboundRef = dt['InboundForecastReference']
                    inboundQty = dt['Quantity'] # Concluded: NO partial qty shipment
                    monta_create_date = self.env['picking.from.odooto.monta'].convert_TZ_UTC(dt['Created'])

                    odoo_inbound_obj = self.env['stock.move.from.odooto.monta'].search(
                        [('product_id.default_code', '=', sku),
                         ('monta_move_id.monta_order_name', '=', inboundRef)])


                    if inboundRef != 'P00206 MI00203': continue

                    if odoo_inbound_obj:
                        picking_obj = odoo_inbound_obj.move_id.picking_id
                        message = 'Inbound Schedular Batches Response: '+json.dumps(dt)
                        odoo_inbound_obj.monta_move_id.write_response(message)
                        odoo_inbound_lines_obj |= odoo_inbound_obj
                        if odoo_inbound_obj.monta_inbound_line_ids.\
                                filtered(lambda rec: rec.inbound_id == str(inboundID)):
                            continue
                        inbound_data = {'monta_move_line_id': odoo_inbound_obj.id,
                                        'inbound_id': inboundID,
                                        'inbound_quantity': inboundQty}

                        # Tracked SKU:
                        if dt.get('Batch', False):
                            batch_ref = dt['Batch']['Reference']
                            inbound_data['monta_batch_ids'] = [(0, 0,
                                                                {'batch_ref':batch_ref,
                                                                 'batch_quantity':dt['Batch']['Quantity'],
                                                                 'monta_create_date':monta_create_date})]
                        else: # Non Tracking SKU
                            if self.product_id.product_tmpl_id.tracking == 'none':
                                odoo_inbound_obj.done_quantity = inboundQty
                                odoo_inbound_obj.monta_shipped_date = monta_create_date

                        self.create(inbound_data)

                except Exception as e:
                    error_message = "\nError: Monta Inbound scheduler %s,\n" % (e)
                    _logger.info(
                        error_message
                    )
                    # picking_obj.post_admin_notification(error_message, 'Inbound')
                    picking_obj.message_post(body=_("%s" % (error_message)))

            if response_data:
                new_inbound_id = False
                inboundIds = [int(id) for id in self.search([]).filtered(lambda l: l.inbound_id).mapped('inbound_id')]
                if inboundIds:
                    new_inbound_id = max(inboundIds)
                elif monta_inbound_ids:
                    new_inbound_id = max(monta_inbound_ids)
                if new_inbound_id:
                    config.write({'inbound_id':new_inbound_id})

                if odoo_inbound_lines_obj:
                    self.validate_picking_from_monta_qty(inboundMoveData=odoo_inbound_lines_obj)
