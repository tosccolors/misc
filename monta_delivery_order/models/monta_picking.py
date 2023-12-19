from odoo import api, fields, models, _
import requests
from requests.auth import HTTPBasicAuth
from odoo.exceptions import AccessError
import json
import logging
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

        #only for outbound batches
        if '/batches' in method:
            url = "https://api-v6.monta.nl"
        # ends

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
                    ('inbounds' in method or '/batches' in method or '/products' in method):
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
        payload = {
            "WebshopOrderId": self.monta_order_name,
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

    @api.model
    def _cron_monta_get_outbound_batches(self):
        method = "order/%s/batches"
        monta_move_obj = self.env['stock.move.from.odooto.monta']
        monta_outbond_obj = self.env['monta.stock.lot']
        outboundMoveData = {}
        for obj in self.search([('picking_id.picking_type_code', '=', 'outgoing'),
                                ('picking_id.state', 'not in', ('draft', 'done', 'cancel')), ('status', '=', 'successful')]):
            try:
                orderNum = obj.monta_order_name
                response = self.call_monta_interface("GET", method%orderNum)
                if response.status_code == 200:
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
                            # batch created
                            monta_outbond_obj.create(data)

                            move_obj = odoo_outbound_line.move_id
                            if outboundMoveData.get((move_obj, batch_ref), False):
                                outboundMoveData[(move_obj, batch_ref)] +=  qty
                            else:
                                outboundMoveData[(move_obj, batch_ref)] = qty
            except Exception as e:
                _logger.info(
                    "\nError: Monta Outbound scheduler %s\n,"%(e)
                )
        if outboundMoveData:
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

    # def create_lot_from_batch(self, product, move_obj, batch_ref, qty):
    #     lot_number = product.default_code + '_' + batch_ref
    #     lot_obj = self.env['stock.lot']
    #     quant = self.env['stock.quant']
    #     lot = lot_obj.search(
    #         [('name', '=', lot_number), ('product_id', '=', product.id),
    #          ('company_id', '=', move_obj.company_id.id)])
    #     if lot:
    #         line_fields = [f for f in quant._fields.keys()]
    #         quantData = quant.with_context(self.env.context.copy()).default_get(line_fields)
    #         quantData.update(
    #             {'product_id': product.id,
    #              'location_id': move_obj.location_dest_id.id,
    #              'quantity': qty,
    #              'inventory_quantity': qty,
    #              'lot_id': lot.id})
    #         quant.create(quantData)
    #     else:
    #         self.env['stock.lot'].create(
    #             {'name': lot_number,
    #              'ref': batch_ref,
    #              'product_id': product.id,
    #              'company_id': move_obj.company_id.id})
    #     return


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

    def validate_picking_from_monta_qty(self, inboundMoveData={}, outboundMoveData={}):
        picking_obj = self.env['stock.picking']
        backorderConfirmObj = self.env['stock.backorder.confirmation']
        exception_picking_data = {}
        monta_obj = self.env['picking.from.odooto.monta']

        def _assign_lot(moveObj, lotRef, qty):
            moveObj.move_line_ids.unlink()

            product = moveObj.product_id
            picking = moveObj.picking_id

            data = {'picking_id': picking.id,
                    'product_id': product.id,
                    'qty_done': qty}

            if picking.picking_type_code == 'incoming':
                data.update({'lot_name': lotRef})
            elif picking.picking_type_code == 'outgoing':
                lot = self.env['stock.lot'].search(
                    [('name', '=', lotRef),('product_id', '=', product.id)
                     ('company_id', '=', moveObj.company_id.id)])
                if lot:
                    data.update({'lot_id': lot.id})

            if ('lot_name' in data) or ('lot_id' in data):
                moveObj.write({'move_line_ids': [(0, 0, data)]})

        # GET inbound
        for inboundObj, moveDt in inboundMoveData.items():
            moveObj = moveDt[0]
            inboundQty = moveDt[1]
            batchRef = moveObj.product_id.default_code + '_' + moveDt[2]
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
            batchRef = moveObj.product_id.default_code + '_' + keys[1]
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
                ctx = res['context']
                # create backorder and process it
                line_fields = [f for f in backorderConfirmObj._fields.keys()]
                backOrderData = backorderConfirmObj.with_context(ctx).default_get(line_fields)
                backOrderId = backorderConfirmObj.with_context(ctx).create(backOrderData)
                backOrderId.with_context(ctx).process()

                #Validated backorder in order to sync to Monta
                backOrderPicking = self.env['stock.picking'].\
                    search([('picking_type_code','=', 'incoming'),
                            ('backorder_id', '=', pickObj.id),
                            ('state', 'in', ('partially_available', 'assigned'))])
                if backOrderPicking:
                    backOrderPicking.transfer_picking_to_monta()
                update_picking_msg[pickObj.monta_log_id] = ''
            except Exception as e:
                pickObj |= pickObj
                msg = ("Error Validating Picking: %s''!!\n" % (e))
                update_picking_msg[pickObj.monta_log_id] = msg

        for monta_obj, message in update_picking_msg.items():
            monta_obj.write({'message':message})


    # def validate_picking_from_monta_qty(self, inboundMoveData={}, outboundMoveData={}):
    #     picking_obj = self.env['stock.picking']
    #     backorderConfirmObj = self.env['stock.backorder.confirmation']
    #     msg = ''
    #     monta_obj = self.env['picking.from.odooto.monta']
    #     def _assign_lot(moveObj, batchRef, qty):
    #         if not moveObj.move_line_ids:
    #             lot = self.env['stock.lot'].search(
    #                 [('name', '=', batchRef), ('company_id', '=', moveObj.company_id.id)], order='id Desc', limit=1)
    #             moveObj.quantity_done = qty  # must update before lot number
    #             for move_line in moveObj.move_line_ids:
    #                 move_line.lot_id = lot.id
    #                 move_line.qty_done = qty # inbound/outbound qty variable
    #         else:
    #             for move_line in moveObj.move_line_ids:
    #                 move_line.lot_name = batchRef
    #                 move_line.qty_done = inboundQty  # inbound/outbound qty variable
    #
    #     #GET inbound
    #     for inboundObj, moveDt in inboundMoveData.items():
    #         moveObj = moveDt[0]
    #         inboundQty = moveDt[1]
    #         batchRef = moveObj.product_id.default_code + '_' + moveDt[2]
    #         monta_obj |= moveObj.picking_id.monta_log_id
    #         try:
    #             if moveObj.state in ('confirmed', 'partially_available', 'assigned'):
    #                 _assign_lot(moveObj, batchRef, inboundQty)
    #                 ## moveObj.move_line_ids.\
    #                 ##     create({'move_id':moveObj.id, 'lot_name':batchRef, 'qty_done':inboundQty}) #create move line and add batch ref for lot/serial number
    #                 # for move_line in moveObj.move_line_ids:
    #                 #     move_line.lot_name = batchRef
    #                 #     move_line.qty_done = inboundQty  # inbound qty variable
    #                 picking_obj |= moveObj.picking_id
    #         except Exception as e:
    #             msg += "Error: Inbound lot/serial number assigning: %s''!!\n" % (e)
    #
    #     # GET Outbound
    #     for keys, qty in outboundMoveData.items():
    #         moveObj = keys[0]
    #         monta_obj |= moveObj.picking_id.monta_log_id
    #         batchRef = moveObj.product_id.default_code + '_' + keys[1]
    #         try:
    #             # lot = self.env['stock.lot'].search([('name', '=', batchRef),  ('company_id', '=', moveObj.company_id.id)], order='id Desc', limit=1)
    #             if moveObj.state in ('confirmed', 'partially_available', 'assigned'):
    #                 _assign_lot(moveObj, batchRef, inboundQty)
    #                 # # moveObj.quantity_done = qty  # outbound qty variable
    #                 # # moveObj.move_line_ids.\
    #                 # #     create({'move_id':moveObj.id, 'lot_name':batchRef, 'qty_done':qty}) #create move line and add batch ref for lot/serial number
    #                 # moveObj.quantity_done = qty # must update before lot number
    #                 # for move_line in moveObj.move_line_ids:
    #                 #     # move_line.lot_name = batchRef
    #                 #     move_line.lot_id = lot.id
    #                 #     move_line.qty_done = qty
    #
    #                 picking_obj |= moveObj.picking_id
    #         except Exception as e:
    #             msg += "Error: Outbound lot/serial number assigning: %s''!!\n" % (e)
    #
    #     for pickObj in picking_obj:
    #         monta_obj |= pickObj.monta_log_id
    #         try:
    #             res = pickObj.button_validate()
    #             if res is True:
    #                 return res
    #             ctx = res['context']
    #             # create backorder and process it
    #             line_fields = [f for f in backorderConfirmObj._fields.keys()]
    #             backOrderData = backorderConfirmObj.with_context(ctx).default_get(line_fields)
    #             backOrderId = backorderConfirmObj.with_context(ctx).create(backOrderData)
    #             backOrderId.with_context(ctx).process()
    #
    #             #Validated backorder in order to sync to Monta
    #             backOrderPicking = self.env['stock.picking'].search([('picking_type_code','=', 'incoming'),('backorder_id', '=', pickObj.id), ('state', 'in', ('partially_available', 'assigned'))])
    #             if backOrderPicking:
    #                 backOrderPicking.transfer_picking_to_monta()
    #         except Exception as e:
    #             msg +=("Error Validating Picking: %s''!!\n" % (e))
    #
    #     if moveObj:
    #         moveObj.write({'message':msg})

    @api.model
    def _cron_monta_get_inbound(self):
        self_obj = self.search([])
        method = 'inbounds'
        config = self.env['monta.config'].search([], limit=1)
        if config.inbound_id:
            method = "inbounds?sinceid=" + config.inbound_id
        response = self.env['picking.from.odooto.monta'].call_monta_interface("GET", method)
        inboundMoveData = {}
        if response.status_code == 200:
            response_data = json.loads(response.text)
            for dt in response_data:
                try:
                    inboundID = dt['Id']
                    sku = dt['Sku']
                    inboundRef = dt['InboundForecastReference']
                    inboundQty = dt['Quantity']
                    odoo_inbound_obj = self.env['stock.move.from.odooto.monta'].search(
                        [('product_id.default_code', '=', sku), ('monta_move_id.monta_order_name', '=', inboundRef)])
                    if odoo_inbound_obj:
                        inbound_data = {'monta_move_line_id': odoo_inbound_obj.id,'inbound_id': inboundID, 'inbound_quantity': inboundQty}
                        batch_ref = False
                        if dt.get('Batch', False):
                            batch_ref = dt['Batch']['Reference']
                            inbound_data['monta_batch_ids'] = [(0, 0, {'batch_ref':batch_ref, 'batch_quantity':dt['Batch']['Quantity']})]
                        newObj = self.create(inbound_data)

                        inboundMoveData[newObj]=[odoo_inbound_obj.move_id, inboundQty, batch_ref]
                except Exception as e:
                    _logger.info(
                        "\nError: Monta Inbound scheduler %s,\n" % (e)
                    )

        inboundIds = [int(id) for id in self.search([]).filtered(lambda l: l.inbound_id).mapped('inbound_id')]
        inbound_id = max(inboundIds) if inboundIds else False
        config.write({'inbound_id':inbound_id})
        if inboundMoveData:
            self.validate_picking_from_monta_qty(inboundMoveData=inboundMoveData)


# class MontaStockLot(models.Model):
#     _name = 'monta.stock.lot'
#     _order = 'create_date desc'
#     _rec_name = 'batch_ref'
# 
#     batch_id = fields.Char('Batch ID')
#     batch_ref = fields.Char(string='Title/Batch Ref')
#     batch_quantity = fields.Float(string='Batch Quantity')
#     monta_inbound_id = fields.Many2one('monta.inboundto.odoo.move')
#     monta_outbound_id = fields.Many2one('stock.move.from.odooto.monta')
# 
# 
#     @api.model
#     def create(self, vals):
#         res = super().create(vals)
#         params = []
#         batch_ref = res.batch_ref
#         if res.monta_inbound_id:
#             product = res.monta_inbound_id.product_id
#             move_obj = res.monta_inbound_id.monta_move_line_id.move_id
#             qty = res.monta_inbound_id.inbound_quantity
#             params.append(product, move_obj, qty)
# 
#         if res.monta_outbound_id:
#             product = res.monta_outbound_id.product_id
#             move_obj = res.monta_outbound_id.move_id
#             qty = res.batch_quantity
#             params.append(product, move_obj, qty)
# 
#         if params:
#             self.env['stock.move.from.odooto.monta'].create_lot_from_batch(params[0], params[1], res.batch_ref, params[2])
#         return res


# class MontaInboundBatchtoOdooMove(models.Model):
#     _name = 'monta.inbound.batch'
#     _order = 'create_date desc'
#     _rec_name = 'monta_inbound_id'
#
#     monta_inbound_id = fields.Many2one('monta.inboundto.odoo.move', required=True)
#     batch_ref = fields.Char('Batch Ref#')
#     batch_quantity = fields.Float(string='Batch Quantity')
#
#     @api.model
#     def create(self, vals):
#         res = super().create(vals)
#         product = res.monta_inbound_id.product_id
#         move_obj = res.monta_inbound_id.monta_move_line_id.move_id
#         self.env['stock.move.from.odooto.monta'].create_lot_from_batch(product, move_obj, res.batch_ref, res.monta_inbound_id.inbound_quantity)
#         return res
#
# class MontaOutboundBatchtoOdooMove(models.Model):
#     _name = 'monta.outbound.batch'
#     _order = 'create_date desc'
#     _rec_name = 'monta_outbound_id'
#
#     monta_outbound_id = fields.Many2one('stock.move.from.odooto.monta', required=True)
#     batch_id = fields.Char('Batch ID')
#     title = fields.Char(string='Title/Batch Ref')
#     batch_quantity = fields.Float(string='Batch Quantity')
#
#     @api.model
#     def create(self, vals):
#         res = super().create(vals)
#         product = res.monta_outbound_id.product_id
#         move_obj = res.monta_outbound_id.move_id
#         self.env['stock.move.from.odooto.monta'].create_lot_from_batch(product, move_obj, res.title, res.batch_quantity)
#         return res


