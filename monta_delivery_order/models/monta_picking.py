from odoo import api, fields, models, _
import requests
from requests.auth import HTTPBasicAuth
from odoo.exceptions import AccessError
import json


class PickingfromOdootoMonta(models.Model):
    _name = 'picking.from.odooto.monta'
    _order = 'create_date desc'

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
    sale_id = fields.Many2one('sale.order', related="picking_id.sale_id")
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
    status = fields.Selection([('draft', 'Draft'), ('successful', 'Successful'), ('failed', 'Failed')], string='Status',
                              required=True, readonly=True, store=True, compute=_compute_response)


    def call_monta_interface(self, payload, request, method):
        config = self.env['monta.config'].search([], limit=1)
        payload = json.dumps(payload)
        self.write({"json_payload": payload})
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

            if response.status_code == 200 and 'rest/v5/inbounds' == method:
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

    def monta_good_receipt_content(self):
        config = self.env['monta.config'].search([], limit=1)
        planned_shipment_date = self.planned_shipment_date.isoformat()
        shipped = self.shipped.isoformat() if self.shipped else planned_shipment_date
        delivery_add = self.partner_delivery_address_id
        invoice_add  = self.partner_invoice_address_id if self.sale_id else self.partner_delivery_address_id
        payload = {
            "WebshopOrderId": self.picking_id.name,
            "Origin": config.origin,
            "ConsumerDetails":{
                "DeliveryAddress": {
                        "Company": delivery_add.name,
                        "FirstName": delivery_add.firstname,
                        "MiddleName": '',
                        "LastName": delivery_add.lastname,
                        "Street": delivery_add.street if delivery_add.street else ' '+' '+delivery_add.street2 if delivery_add.street2 else ' ',
                        "HouseNumber": '',
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
                    "Street": invoice_add.street or '' + ' ' + invoice_add.street2 or '',
                    "HouseNumber": '',
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
            "PickbonIds": ''
        }

        for line in self.monta_stock_move_ids:
            payload['Lines'].append({
                "Sku": line.product_id.default_code,
                "OrderedQuantity": line.ordered_quantity
            })
        self.call_monta_interface(payload, "POST", "rest/v5/order")

    def monta_inbound_forecast_content(self):
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
        response = self.call_monta_interface(payload, "POST", "rest/v5/inboundforecast/group")
        return response



class PickingLinefromOdootoMonta(models.Model):
    _name = 'stock.move.from.odooto.monta'
    _order = 'create_date desc'

    move_id = fields.Many2one('stock.move', required=True)
    monta_move_id = fields.Many2one('picking.from.odooto.monta', required=True)
    product_id = fields.Many2one('product.product', related='move_id.product_id')
    ordered_quantity = fields.Float(related='move_id.product_qty', string='Ordered Quantity')
    monta_inbound_forecast_id = fields.Char("Monta Inbound Forecast Id")
    inbound_id = fields.Char('Inbound ID')

    @api.model
    def _cron_monta_get_inbound(self):
        self_obj = self.search([])
        inboundIds = [int(id) for id in self_obj.filtered(lambda l: l.inbound_id).mapped('inbound_id')]
        inbound_id = max(inboundIds) if inboundIds else False
        method = 'rest/v5/inbounds'
        if inbound_id:
            method ="rest/v5/inbounds?sinceid="+str(inbound_id)
        response = self.env['picking.from.odooto.monta'].call_monta_interface({}, "GET", method)
        if response.status_code == 200:
            response_data = json.loads(response.text)
            for dt in response_data:
                inboundID = dt['Id']
                sku = dt['Sku']
                inboundRef = dt['InboundForecastReference']
                odoo_inbound_obj = self.search([('product_id.default_code', '=', sku), ('monta_move_id.picking_id.name', '=', inboundRef)])
                if odoo_inbound_obj:
                    odoo_inbound_obj.write({'inbound_id':inboundID})

