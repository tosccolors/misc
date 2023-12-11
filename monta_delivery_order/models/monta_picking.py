from odoo import api, fields, models, _
import requests
from requests.auth import HTTPBasicAuth
from odoo.exceptions import AccessError
import json


class PickingfromOdootoMonta(models.Model):
    _name = 'picking.from.odooto.monta'
    _order = 'create_date desc'
    _rec_name = 'picking_id'

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
    # outbound_batch = fields.Boolean()


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
            if response.status_code == 200 and ('rest/v5/inbounds' == method or '/batches' in method):
                return response

            dic ={
                'monta_response_code': response.status_code,
                'monta_response_message': response.text,
            }
            if response.status_code == 200 and method == 'rest/v5/inboundforecast/group':
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
                _('Error Roularta Interface call: %s') % (e))
            # raise FailedJobError(
            #     _('Error Roularta Interface call: %s') % (e))
        return response

    def monta_good_receipt_content(self, button_action=False):
        config = self.env['monta.config'].search([], limit=1)
        planned_shipment_date = self.planned_shipment_date.isoformat()
        shipped = self.shipped.isoformat() if self.shipped else planned_shipment_date
        delivery_add = self.partner_delivery_address_id
        invoice_add  = self.partner_invoice_address_id if self.sale_id else self.partner_delivery_address_id
        payload = {
            "WebshopOrderId": self.picking_id.name,
            "Reference": self.client_order_ref,
            "Origin": config.origin,
            "ConsumerDetails":{
                "DeliveryAddress": {
                        "Company": delivery_add.name,
                        "FirstName": delivery_add.firstname,
                        "MiddleName": '',
                        "LastName": delivery_add.lastname,
                        "Street": (delivery_add.street_name if delivery_add.street_name else ' ')+' '+(delivery_add.street2 if delivery_add.street2 else ' '),
                        "HouseNumber": (delivery_add.street_number if delivery_add.street_number else ' ') + '-'+ (delivery_add.street_number2 if delivery_add.street_number2 else ' '),
                        "HouseNumberAddition": '',
                        "PostalCode": delivery_add.zip,
                        "City": delivery_add.city,
                        "State": delivery_add.state_id.code,
                        "CountryCode": delivery_add.country_id.code,
                        "PhoneNumber": delivery_add.mobile,
                        "EmailAddress": delivery_add.email
                },
                "InvoiceAddress": {
                    "Company": invoice_add.name,
                    "FirstName": invoice_add.firstname,
                    "MiddleName": '',
                    "LastName": invoice_add.lastname,
                    "Street":   (invoice_add.street_name if invoice_add.street_name else ' ')+' '+(invoice_add.street2 if invoice_add.street2 else ' '),
                    "HouseNumber": (invoice_add.street_number if invoice_add.street_number else ' ') + '-'+ (invoice_add.street_number2 if invoice_add.street_number2 else ' '),
                    "HouseNumberAddition": '',
                    "PostalCode": invoice_add.zip,
                    "City": invoice_add.city,
                    "State": invoice_add.state_id.code,
                    "CountryCode": invoice_add.country_id.code,
                    "PhoneNumber": invoice_add.mobile,
                    "EmailAddress": invoice_add.email
                },
                "InvoiceDebtorNumber": '',
                "B2B": False,
                "ShippingComment": self.shipping_comment
            },
            "PlannedShipmentDate": planned_shipment_date,
            "ShipOnPlannedShipmentDate": planned_shipment_date,
            "Blocked": False,
            "BlockedMessage": '',
            "Quarantaine": False,
            "DeliveryDateRequested": planned_shipment_date,
            "Lines":[],
            "Picking": True,
            "Picked": '',
            "Shipped": shipped,
            "PackingServiceText": '',
            "Family": '',
            "Comment":self.client_order_ref,
            "PickbonIds": ''
        }

        for line in self.monta_stock_move_ids:
            payload['Lines'].append({
                "Sku": line.product_id.default_code,
                "OrderedQuantity": int(line.ordered_quantity)
            })

        payload = json.dumps(payload)
        self.write({"json_payload": payload})
        if not button_action:
            self.call_monta_interface("POST", "rest/v5/order")

    def monta_inbound_forecast_content(self, button_action=False):
        planned_shipment_date = self.planned_shipment_date.isoformat()
        payload = {
                "Reference": self.picking_id.name,
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
            response = self.call_monta_interface("POST", "rest/v5/inboundforecast/group")
            return response

    def generate_payload(self):
        if self.picking_type_code == 'outgoing' and self.sale_id:
            self.monta_good_receipt_content(True)
        elif self.picking_type_code == 'incoming' and self.purchase_id:
            self.monta_inbound_forecast_content(True)

    def action_call_monta_interface(self):
        if self.picking_type_code == 'outgoing' and self.sale_id:
            self.call_monta_interface("POST", "rest/v5/order")
        elif self.picking_type_code == 'incoming' and self.purchase_id:
            self.call_monta_interface("POST", "rest/v5/inboundforecast/group")

    @api.model
    def _cron_monta_get_outbound_batches(self):
        # self_obj = self.search([])
        method = "order/%s/batches"
        monta_move_obj = self.env['stock.move.from.odooto.monta']
        monta_outbond_obj = self.env['monta.outbound.batch']
        for obj in self.search([('picking_id.picking_type_code', '=', 'outgoing'),('picking_id.state', '=', 'assigned'), ('status', '=', 'successful')]):
        # for obj in self.search([('picking_id.picking_type_code', '=', 'outgoing')]):
            orderNum = obj.picking_id.name.replace('/', '')
            response = self.call_monta_interface("GET", method%orderNum)
            if response.status_code == 200:
                response_data = json.loads(response.text)
                for line in response_data.get('BatchLines', []):
                    sku = line['Sku']
                    batch_content = line['BatchContent']
                    odoo_outbound_line = monta_move_obj.search(
                        [('product_id.default_code', '=', sku), ('monta_move_id.picking_id.name', '=', obj.picking_id.name)])
                    if odoo_outbound_line:
                        data = {'batch_id':batch_content['Id'],
                                'title':batch_content['Title'],
                                'monta_outbound_id': odoo_outbound_line.id}
                        monta_outbond_obj.create(data)


class PickingLinefromOdootoMonta(models.Model):
    _name = 'stock.move.from.odooto.monta'
    _order = 'create_date desc'
    _rec_name = 'monta_move_id'

    move_id = fields.Many2one('stock.move', required=True)
    monta_move_id = fields.Many2one('picking.from.odooto.monta', required=True)
    product_id = fields.Many2one('product.product', related='move_id.product_id')
    ordered_quantity = fields.Float(related='move_id.product_qty', string='Ordered Quantity')
    monta_inbound_forecast_id = fields.Char("Monta Inbound Forecast Id")
    monta_inbound_line_ids = fields.One2many('monta.inboundto.odoo.move', 'monta_move_line_id')
    monta_outbound_batch_ids = fields.One2many('monta.outbound.batch', 'monta_outbound_id')

    # inbound_id = fields.Char('Inbound ID')


class MontaInboundtoOdooMove(models.Model):
    _name = 'monta.inboundto.odoo.move'
    _order = 'create_date desc'
    _rec_name = 'monta_move_line_id'

    monta_move_line_id = fields.Many2one('stock.move.from.odooto.monta', required=True)
    inbound_id = fields.Char('Inbound ID')
    product_id = fields.Many2one('product.product', related='monta_move_line_id.product_id')
    inbound_quantity = fields.Float(string='Inbound Quantity')
    monta_batch_ids = fields.One2many('monta.inbound.batch', 'monta_inbound_id')

    def validate_picking_from_inbound_qty(self, inboundMoveData={}):
        picking_obj = self.env['stock.picking']
        backorderConfirmObj = self.env['stock.backorder.confirmation']

        for inboundObj, moveDt in inboundMoveData.items():
            moveObj = moveDt[0]
            inboundQty = moveDt[1]
            if moveObj.state in ('partially_available', 'assigned'):
                for move_line in moveObj.move_line_ids:
                    move_line.qty_done = inboundQty  # inbound qty variable
                picking_obj |= moveObj.picking_id

        for pickObj in picking_obj:
            res = pickObj.button_validate()
            if res is True:
                return res
            ctx = res['context']
            # create backorder and process it
            line_fields = [f for f in backorderConfirmObj._fields.keys()]
            backOrderData = backorderConfirmObj.with_context(ctx).default_get(line_fields)
            backOrderId = backorderConfirmObj.with_context(ctx).create(backOrderData)
            backOrderId.with_context(ctx).process()

            #Validated backorder in order to sync to Monta
            backOrderPicking = self.env['stock.picking'].search([('picking_type_code','=', 'incoming'),('backorder_id', '=', pickObj.id), ('state', 'in', ('partially_available', 'assigned'))])
            if backOrderPicking:
                backOrderPicking.transfer_picking_to_monta()
            return True
        return False

    @api.model
    def _cron_monta_get_inbound(self):
        self_obj = self.search([])
        inboundIds = [int(id) for id in self_obj.filtered(lambda l: l.inbound_id).mapped('inbound_id')]
        inbound_id = max(inboundIds) if inboundIds else False
        method = 'rest/v5/inbounds'
        if inbound_id:
            method = "rest/v5/inbounds?sinceid=" + str(inbound_id)
        response = self.env['picking.from.odooto.monta'].call_monta_interface("GET", method)
        inboundMoveData = {}
        if response.status_code == 200:
            response_data = json.loads(response.text)
            for dt in response_data:
                inboundID = dt['Id']
                sku = dt['Sku']
                inboundRef = dt['InboundForecastReference']
                inboundQty = dt['Quantity']
                odoo_inbound_obj = self.env['stock.move.from.odooto.monta'].search(
                    [('product_id.default_code', '=', sku), ('monta_move_id.picking_id.name', '=', inboundRef)])
                if odoo_inbound_obj:
                    inbound_data = {'monta_move_line_id': odoo_inbound_obj.id,'inbound_id': inboundID, 'inbound_quantity': inboundQty}
                    if dt.get('Batch', False):
                        inbound_data['monta_batch_ids'] = [(0, 0, {'batch_id':dt['Batch']['Reference'], 'batch_quantity':dt['Batch']['Quantity']})]
                    newObj = self.create(inbound_data)

                    inboundMoveData[newObj]=[odoo_inbound_obj.move_id, inboundQty]
        if inboundMoveData:
            self.validate_picking_from_inbound_qty(inboundMoveData)


class MontaInboundBatchtoOdooMove(models.Model):
    _name = 'monta.inbound.batch'
    _order = 'create_date desc'
    _rec_name = 'monta_inbound_id'

    monta_inbound_id = fields.Many2one('monta.inboundto.odoo.move', required=True)
    batch_id = fields.Char('Batch ID')
    batch_quantity = fields.Float(string='Batch Quantity')


class MontaOutboundBatchtoOdooMove(models.Model):
    _name = 'monta.outbound.batch'
    _order = 'create_date desc'
    _rec_name = 'monta_outbound_id'

    monta_outbound_id = fields.Many2one('stock.move.from.odooto.monta', required=True)
    batch_id = fields.Char('Batch ID')
    title = fields.Float(string='Title')


