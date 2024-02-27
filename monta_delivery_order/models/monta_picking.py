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
                
    @api.depends('picking_id')
    def _compute_order_name(self):
        for pick in self:
            pick.monta_order_name = pick.picking_id.name.replace('/', '')

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
    picking_monta_response = fields.Boolean(compute=_compute_response, default=False, store=True, string='Roularta Response')
    json_payload = fields.Text('Payload')
    client_order_ref = fields.Char(string="Customer Reference", related="picking_id.client_order_ref")
    status = fields.Selection([('draft', 'Draft'), ('successful', 'Successful'), ('failed', 'Failed')], string='Status',
                              required=True, readonly=True, store=True, compute=_compute_response)
    monta_order_name = fields.Char(string="Monta Order Name", compute=_compute_order_name, store=True)
    message = fields.Char('Error/Exception Message')

    def call_monta_interface(self, request, method):
        config = self.env['monta.config'].search([], limit=1)
        payload = self.json_payload
        headers = {
            'Content-Type': 'application/json'
        }

        url = config.host

        # GET inboundforecast/group/
        if 'api-v6.monta.nl' in method:
            url = "https://api-v6.monta.nl"
            method = method.split(url)[1]
        elif '/batches' in method :#only for outbound batches
            url = "https://api-v6.monta.nl"

        if url.endswith("/"):
            url += method
        else:
            url += '/'+method
        user = config.username
        pwd = config.password
        response = False
        try:
            response = requests.request(request, url, headers=headers, data=payload, auth=HTTPBasicAuth(user, pwd))
            if response.status_code == 200 and \
                    ('inbounds' in method or '/batches' in method or '/product' in method
                     or 'api-v6.monta.nl' in url):
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
            self.write(dic)
        except Exception as e:
            raise AccessError(
                _('Error Monta Interface call: %s') % (e))
        return response

    def monta_good_receipt_content(self, button_action=False):
        config = self.env['monta.config'].search([], limit=1)
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
            "ShipOnPlannedShipmentDate": planned_shipment_date,
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

        if self.sale_id.carrier_id:
            delivery_method = self.sale_id.carrier_id
            payload['AllowedShippers'].append(
                delivery_method.monta_shipper_code
            )

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

    def generate_payload(self):
        if self.picking_type_code == 'outgoing' and self.sale_id:
            self.monta_good_receipt_content(True)
        elif self.picking_type_code == 'incoming' and self.purchase_id:
            self.monta_inbound_forecast_content(True)

    def action_call_monta_interface(self):
        if self.picking_type_code == 'outgoing' and self.sale_id:
            self.call_monta_interface("POST", "order")
        elif self.picking_type_code == 'incoming' and self.purchase_id:
            self.call_monta_interface("POST", "inboundforecast/group")

    def convert_TZ_UTC(self, TZ_datetime):
        shipped_date = datetime.strptime(TZ_datetime, '%Y-%m-%dT%H:%M:%S.%f').strftime('%Y-%m-%d %H:%M:%S')
        shipped_date = datetime.strptime(shipped_date, '%Y-%m-%d %H:%M:%S')
        tz_name = self.env.context.get('tz') or self.env.user.tz
        user_tz = pytz.timezone(tz_name)
        utc = pytz.utc
        dt = user_tz.localize(shipped_date).astimezone(utc).strftime('%Y-%m-%d %H:%M:%S')
        return dt

    @api.model
    def _cron_monta_get_outbound_batches(self):
        method = "order/%s/batches"
        monta_move_obj = self.env['stock.move.from.odooto.monta']
        monta_outbond_obj = self.env['monta.stock.lot']
        stockMove = self.env['stock.move']
        outboundMoveData = {}
        for obj in self.search([('picking_id.picking_type_code', '=', 'outgoing'),
                                ('picking_id.state', 'not in', ('draft', 'done', 'cancel')), ('status', '=', 'successful')]):
            try:
                orderNum = obj.monta_order_name
                response = self.call_monta_interface("GET", method%orderNum)
                response_order_info = self.call_monta_interface("GET", "order/%s"%orderNum)
                if response.status_code == 200:
                    shipped_date = False
                    if response_order_info.status_code == 200:
                        response_order_info_data = json.loads(response_order_info.text)
                        shipped_date = self.convert_TZ_UTC(response_order_info_data['Shipped'])
                    response_data = json.loads(response.text)
                    for line in response_data.get('BatchLines', []):
                        sku = line['Sku']
                        batch_content = line['BatchContent']
                        qty = abs(int(line['Quantity']))
                        odoo_outbound_line = monta_move_obj.search(
                            [('product_id.default_code', '=', sku), ('monta_move_id.monta_order_name', '=', obj.monta_order_name)])
                        if odoo_outbound_line:
                            batch_ref = batch_content['Title']
                            data = {'batch_id':batch_content['Id'],
                                    'batch_ref':batch_content['Title'],
                                    'batch_quantity':qty,
                                    'monta_outbound_id': odoo_outbound_line.id}
                            if shipped_date:
                                data.update({'monta_create_date': shipped_date})
                            # batch created
                            monta_outbond_obj.create(data)

                            move_obj = odoo_outbound_line.move_id
                            stockMove |= move_obj
                            if outboundMoveData.get((move_obj, batch_ref), False):
                                outboundMoveData[(move_obj, batch_ref)] +=  qty
                            else:
                                outboundMoveData[(move_obj, batch_ref)] = qty
            except Exception as e:
                _logger.info(
                    "\nError: Monta Outbound scheduler %s\n,"%(e)
                )
        if outboundMoveData:
            # stockMove.mapped('move_line_ids').unlink()
            self.env['monta.inboundto.odoo.move'].validate_picking_from_monta_qty(outboundMoveData=outboundMoveData)


class PickingLinefromOdootoMonta(models.Model):
    _name = 'stock.move.from.odooto.monta'
    _order = 'create_date desc'
    _rec_name = 'monta_move_id'
    _description = 'Move Odoo To Monta'

    move_id = fields.Many2one('stock.move', required=True)
    monta_move_id = fields.Many2one('picking.from.odooto.monta', required=True)
    product_id = fields.Many2one('product.product', related='move_id.product_id')
    ordered_quantity = fields.Float(related='move_id.product_qty', string='Ordered Quantity')
    monta_inbound_forecast_id = fields.Char("Monta Inbound Forecast Id")
    monta_inbound_line_ids = fields.One2many('monta.inboundto.odoo.move', 'monta_move_line_id')
    # monta_outbound_batch_ids = fields.One2many('monta.outbound.batch', 'monta_outbound_id')
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
    # monta_batch_ids = fields.One2many('monta.inbound.batch', 'monta_inbound_id')
    monta_batch_ids = fields.One2many('monta.stock.lot', 'monta_inbound_id')

    def apply_backdate(self, pickObj):
        date = False
        if pickObj.picking_type_code == 'outgoing':
            date = max(pickObj.monta_log_id.monta_stock_move_ids.monta_outbound_batch_ids.mapped('monta_create_date'))

        elif pickObj.picking_type_code == 'incoming':
            date = max(pickObj.monta_log_id.monta_stock_move_ids.monta_inbound_line_ids.monta_batch_ids.mapped('monta_create_date'))
        if date:
            pickObj.move_line_ids.write(
                {
                    "date_backdating": date,
                }
            )
        return

    def partial_validation_from_monta(self, pickObj, res):
        backorderConfirmObj = self.env['stock.backorder.confirmation']

        approved = []
        if pickObj.picking_type_code == 'incoming':
            method = "https://api-v6.monta.nl/inboundforecast/group/"+pickObj.name
            response = self.env['picking.from.odooto.monta'].call_monta_interface("GET", method)
            if response.status_code == 200:
                response_data = json.loads(response.text)
                approved = [val['Approved'] for i, val in enumerate(response_data['InboundForecasts']) if not val['Approved']]

        if len(approved) == 0: #for outgoing shipment no check required
            self.apply_backdate(pickObj)
            ctx = res['context']
            # cancel backorder and validate picking
            line_fields = [f for f in backorderConfirmObj._fields.keys()]
            backOrderData = backorderConfirmObj.with_context(ctx).default_get(line_fields)
            backOrderId = backorderConfirmObj.with_context(ctx).create(backOrderData)
            backOrderId.with_context(
                ctx).process_cancel_backorder() # partial force validation create new line with 0 qty done

        return True

    def validate_picking_from_monta_qty(self, inboundMoveData={}, outboundMoveData={}):
        picking_obj = self.env['stock.picking']
        backorderConfirmObj = self.env['stock.backorder.confirmation']
        update_picking_msg = {}
        monta_obj = self.env['picking.from.odooto.monta']

        def _assign_lot(moveObj, lotRef, qty):
            # moveObj.move_line_ids.unlink()

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
                if lot:
                    data.update({'lot_id': lot.id})

            if ('lot_name' in data) or ('lot_id' in data):
                moveObj.write({'move_line_ids': [(0, 0, data)]})

        # GET inbound
        for inboundObj, moveDt in inboundMoveData.items():
            moveObj = moveDt[0]
            inboundQty = moveDt[1]
            # batchRef = moveObj.product_id.default_code + '_' + moveDt[2]
            batchRef = moveDt[2]
            monta_obj |= moveObj.picking_id.monta_log_id
            try:
                if moveObj.state in ('confirmed', 'partially_available', 'assigned'):
                    _assign_lot(moveObj, batchRef, inboundQty)
                    picking_obj |= moveObj.picking_id
                update_picking_msg[moveObj.picking_id.monta_log_id] = ''
            except Exception as e:
                msg = "Error: Inbound lot/serial number assigning: %s''!!\n" % (e)
                update_picking_msg[moveObj.picking_id.monta_log_id] = msg

        # GET Outbound
        for keys, outQty in outboundMoveData.items():
            moveObj = keys[0]
            monta_obj |= moveObj.picking_id.monta_log_id
            # batchRef = moveObj.product_id.default_code + '_' + keys[1]
            batchRef = keys[1]
            try:
                if moveObj.state in ('confirmed', 'partially_available', 'assigned'):
                    _assign_lot(moveObj, batchRef, outQty)
                    picking_obj |= moveObj.picking_id
                update_picking_msg[moveObj.picking_id.monta_log_id] = ''
            except Exception as e:
                msg = "Error: Outbound lot/serial number assigning: %s''!!\n" % (e)
                update_picking_msg[moveObj.picking_id.monta_log_id] = msg

        for pickObj in picking_obj:
            monta_obj |= pickObj.monta_log_id
            try:
                res = pickObj.button_validate()
                if res is True:
                    return res

                self.partial_validation_from_monta(pickObj, res)

                # Disable backorder creation #################
                # ctx = res['context']
                # # create backorder and process it
                # line_fields = [f for f in backorderConfirmObj._fields.keys()]
                # backOrderData = backorderConfirmObj.with_context(ctx).default_get(line_fields)
                # backOrderId = backorderConfirmObj.with_context(ctx).create(backOrderData)
                # backOrderId.with_context(ctx).process()
                #
                # #Validated backorder in order to sync to Monta
                # backOrderPicking = self.env['stock.picking'].\
                #     search([('picking_type_code','=', 'incoming'),
                #             ('backorder_id', '=', pickObj.id),
                #             ('state', 'in', ('partially_available', 'assigned'))])
                # if backOrderPicking:
                #     backOrderPicking.transfer_picking_to_monta()
                # Disable backorder End###############
                update_picking_msg[pickObj.monta_log_id] = ''
            except Exception as e:
                pickObj |= pickObj
                msg = ("Error Validating Picking: %s''!!\n" % (e))
                update_picking_msg[pickObj.monta_log_id] = msg

        for monta_obj, message in update_picking_msg.items():
            monta_obj.write({'message':message})


    @api.model
    def _cron_monta_get_inbound(self):
        # self_obj = self.search([])
        method = 'inbounds'
        config = self.env['monta.config'].search([], limit=1)
        if config.inbound_id:
            method = "inbounds?sinceid=" + config.inbound_id
        response = self.env['picking.from.odooto.monta'].call_monta_interface("GET", method)
        inboundMoveData = {}
        stockMove = self.env['stock.move']
        if response.status_code == 200:
            response_data = json.loads(response.text)
            for dt in response_data:
                try:
                    inboundID = dt['Id']
                    sku = dt['Sku']
                    inboundRef = dt['InboundForecastReference']
                    inboundQty = dt['Quantity']
                    monta_create_date = self.env['picking.from.odooto.monta'].convert_TZ_UTC(dt['Created'])
                    odoo_inbound_obj = self.env['stock.move.from.odooto.monta'].search(
                        [('product_id.default_code', '=', sku), ('monta_move_id.monta_order_name', '=', inboundRef)])
                    if odoo_inbound_obj:
                        inbound_data = {'monta_move_line_id': odoo_inbound_obj.id,'inbound_id': inboundID, 'inbound_quantity': inboundQty}
                        batch_ref = False
                        if dt.get('Batch', False):
                            batch_ref = dt['Batch']['Reference']
                            inbound_data['monta_batch_ids'] = [(0, 0, {'batch_ref':batch_ref, 'batch_quantity':dt['Batch']['Quantity'], 'monta_create_date':monta_create_date})]
                        newObj = self.create(inbound_data)
                        stockMove |= odoo_inbound_obj.move_id
                        inboundMoveData[newObj]=[odoo_inbound_obj.move_id, inboundQty, batch_ref]
                except Exception as e:
                    _logger.info(
                        "\nError: Monta Inbound scheduler %s,\n" % (e)
                    )

        inboundIds = [int(id) for id in self.search([]).filtered(lambda l: l.inbound_id).mapped('inbound_id')]
        inbound_id = max(inboundIds) if inboundIds else False
        config.write({'inbound_id':inbound_id})
        if inboundMoveData:
            # stockMove.mapped('move_line_ids').unlink()
            self.validate_picking_from_monta_qty(inboundMoveData=inboundMoveData)
