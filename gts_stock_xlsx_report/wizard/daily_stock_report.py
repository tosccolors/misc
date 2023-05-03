from odoo import fields, models, api, _
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT
from odoo.tools.float_utils import float_is_zero
from odoo.exceptions import ValidationError
import pytz

import os
import time
import tempfile
import logging
_logger = logging.getLogger('Stock Report')
from datetime import datetime, timedelta
try:
    from StringIO import StringIO
except ImportError:
    from io import StringIO
try:
    import xlwt
    import xlsxwriter
    from xlwt.Utils import rowcol_to_cell
except ImportError:
    _logger.debug('Can not import xlsxwriter`.')
import base64


class daily_stock_report(models.TransientModel):
    _name = "daily.stock.report"

    name = fields.Char('File Name', readonly=True)
    from_date = fields.Date('Start Date')
    to_date = fields.Date('End Date', default=fields.Date.context_today)
    company_id = fields.Many2one('res.company', 'Company', required=True,
                                 default=lambda self: self.env.user.company_id.id)
    warehouse_ids = fields.Many2many('stock.warehouse', 'warehouse_rel_report_wiz', 'wiz_id',
                                     'warehouse_id', 'Warehouses')
    location_ids = fields.Many2many('stock.location', 'location_rel_report_wiz', 'wiz_id',
                                    'location_id', 'Locations')
    location_id = fields.Many2one('stock.location', 'Location')
    product_ids = fields.Many2many('product.product', 'product_rel_report_wiz', 'wiz_id',
                                   'product_id', 'Products')
    product_id = fields.Many2one('product.product', 'Product')
    show_valuation = fields.Boolean('Valuation', default=False,
                                    help='Show valuation of stock?')
    skip_zero_stock = fields.Boolean('Skip Zero Stock?', default=False,
                                    help='Skip locations / products who has 0 stock?')
    all_locations = fields.Boolean('All Locations?', default=False, help='Select to ')
    report_by = fields.Selection([('all', 'Summarised Report'),
                                  ('location_wise', 'Location Wise Report'),
                                  ('detailed_report', 'Detailed Report')],
                                 default='detailed_report', string='Report Type',
                                 help='Select location wise if report is required location wise.')
    warehouse_id = fields.Many2one('stock.warehouse', 'Warehouse')

    @api.constrains('from_date', 'to_date')
    def _check_from_to_date(self):
        for wizard in self:
            if wizard.from_date and wizard.from_date > wizard.to_date:
                raise ValidationError(_("End Date should be greater than or equal to from date!"))

    # def get_locations(self):
    #     location_obj = self.env['stock.location']
    #     locations = location_obj
    #     if self.warehouse_ids:
    #         for w in self.warehouse_ids:
    #             if w.lot_stock_id.usage == 'internal':
    #                 locations += w.lot_stock_id
    #     else:
    #         if self.location_ids:
    #             locations += self.location_ids
    #         else:
    #             locations += location_obj.search([
    #                 ('usage', '=', 'internal'), '|', ('company_id', '=', self.company_id.id),
    #                 ('company_id', '=', False)], order='level asc')
    #     return locations

    def get_locations(self):
        location_obj = self.env['stock.location']
        locations = location_obj
        if self.warehouse_id:
            if self.warehouse_id.lot_stock_id.usage == 'internal':
                locations += self.warehouse_id.lot_stock_id
        else:
            if self.location_ids:
                locations += self.location_ids
            else:
                locations += location_obj.search([
                    ('usage', '=', 'internal'), '|', ('company_id', '=', self.company_id.id),
                    ('company_id', '=', False)], order='level asc')
        if self.report_by == 'detailed_report' and self.location_id:
            locations = self.location_id
        return locations

    def get_child_locations(self, location):
        location_obj = self.env['stock.location']
        child_list = iteration_list = location.ids
        while iteration_list:
            for loc in location_obj.browse(iteration_list):
                if loc.child_ids.filtered(lambda l: l.usage == 'internal'):
                    child_list += loc.child_ids.filtered(lambda l: l.usage == 'internal').ids
                    iteration_list += loc.child_ids.filtered(lambda l: l.usage == 'internal').ids
                iteration_list = list(set(iteration_list))
                if loc.id in iteration_list:
                    iteration_list.remove(loc.id)
        if child_list:
            child_list = list(set(child_list))
        return child_list and location_obj.browse(child_list) or location

    def get_product_available(self, product, from_date=False, to_date=False, location=False,
                              warehouse=False, compute_child=True):
        """ Function to return stock """
        locations = self.get_child_locations(location)
        date_str, date_values = False, False
        where = [tuple(locations.ids), tuple(locations.ids), tuple([product.id])]
        if from_date and to_date:
            date_str = "move.date::DATE>=%s and move.date::DATE<=%s"
            where.append(tuple([from_date]))
            where.append(tuple([to_date]))
            print("where1 ++++++++++++++++++++++++", where)
        elif from_date:
            date_str = "move.date::DATE>=%s"
            date_values = [from_date]
            print("+++++++++++++++++++++===date_str", date_str)
            print("+++++++++++++++++++++===date_values", date_values)
        elif to_date:
            date_str = "move.date::DATE<=%s"
            date_values = [to_date]
            print("+++++++++++++++++++++===date_str1", date_str)
            print("+++++++++++++++++++++===date_values1", date_values)

        if date_values:
            where.append(tuple(date_values))
            print("where ++++++++++++++++++++++++", where)

        self._cr.execute(
            '''select sum(product_qty), product_id, product_uom 
            from stock_move move
            INNER JOIN stock_picking picking ON (move.picking_id = picking.id)
            INNER JOIN stock_picking_type picking_type ON (picking.picking_type_id = picking_type.id)
            where move.location_id NOT IN %s
            and move.location_dest_id IN %s
            and product_id IN %s and move.state = 'done' 
            and move.picking_id is not null
            and move.inventory_id is null
            and move.origin_returned_move_id is null
            '''
            + (date_str and 'and ' + date_str + ' ' or '') + \
            ''' and picking_type.code = 'incoming'
            group by product_id, product_uom''', tuple(where))
        results_incoming_purchases = self._cr.fetchall()
        # print("results_incoming_purchases", results_incoming_purchases)

        self._cr.execute(
            '''select sum(product_qty), product_id, product_uom 
            from stock_move move
            INNER JOIN stock_picking picking ON (move.picking_id = picking.id)
            INNER JOIN stock_picking_type picking_type ON (picking.picking_type_id = picking_type.id)
            where move.location_id NOT IN %s
            and move.location_dest_id IN %s
            and product_id IN %s and move.state = 'done' 
            and move.picking_id is not null
            and move.inventory_id is null
            and move.origin_returned_move_id is not null
            '''
            + (date_str and 'and ' + date_str + ' ' or '') + \
            ''' and picking_type.code = 'incoming'
            group by product_id, product_uom''', tuple(where))
        results_incoming_returns = self._cr.fetchall()
        # print("result incomming return", results_incoming_returns)

        self._cr.execute(
            '''select sum(product_qty), product_id, product_uom 
            from stock_move move 
            INNER JOIN stock_picking picking ON (move.picking_id = picking.id)
            INNER JOIN stock_picking_type picking_type  ON (picking.picking_type_id = picking_type.id)
            where move.location_id IN %s
            and move.location_dest_id NOT IN %s
            and product_id IN %s and move.state = 'done' 
            and move.picking_id is not null
            and move.inventory_id is null
            '''
            + (date_str and 'and ' + date_str + ' ' or '') + \
            ''' and picking_type.code = 'outgoing'
            group by product_id, product_uom''', tuple(where))
        results_outgoing = self._cr.fetchall()
        # print("results_outgoing", results_outgoing)

        self._cr.execute(
            '''select sum(product_qty), product_id, product_uom 
            from stock_move move 
            INNER JOIN stock_picking picking ON (move.picking_id = picking.id)
            INNER JOIN stock_picking_type picking_type ON (picking.picking_type_id = picking_type.id)
            where move.location_id NOT IN %s
            and move.location_dest_id IN %s
            and product_id IN %s and move.state = 'done' 
            and move.picking_id is not null
            and move.inventory_id is null
            '''
            + (date_str and 'and ' + date_str + ' ' or '') + \
            ''' and picking_type.code = 'internal'
            group by product_id, product_uom''', tuple(where))
        results_internal_in = self._cr.fetchall()
        # print("results_internal_in", results_internal_in)

        self._cr.execute(
            '''select sum(product_qty), product_id, product_uom 
            from stock_move move 
            INNER JOIN stock_picking picking ON (move.picking_id = picking.id)
            INNER JOIN stock_picking_type picking_type ON (picking.picking_type_id = picking_type.id)
            where move.location_id IN %s
            and move.location_dest_id NOT IN %s
            and product_id IN %s and move.state = 'done' 
            and move.picking_id is not null
            and move.inventory_id is null
            '''
            + (date_str and 'and ' + date_str + ' ' or '') + \
            ''' and picking_type.code = 'internal'
            group by product_id, product_uom''', tuple(where))
        results_internal_out = self._cr.fetchall()
        # print("results_internal_out", results_internal_out)

        self._cr.execute(
            '''select sum(product_qty), product_id, product_uom 
            from stock_move move 
            where move.location_id NOT IN %s
            and move.location_dest_id IN %s
            and product_id IN %s and move.state = 'done' 
            and move.picking_id is null
            and move.inventory_id is not null
            '''
            + (date_str and 'and ' + date_str + ' ' or '') + \
            '''
            group by product_id, product_uom''', tuple(where))
        results_adjustment_in = self._cr.fetchall()
        # print("results_adjustment_in", results_adjustment_in)

        self._cr.execute(
            '''select sum(product_qty), product_id, product_uom 
            from stock_move move 
            where move.location_id IN %s
            and move.location_dest_id NOT IN %s
            and product_id IN %s and move.state = 'done' 
            and move.picking_id is null
            and move.inventory_id is not null
            '''  + (date_str and 'and ' + date_str + ' ' or '') + \
            ''' group by product_id, product_uom''', tuple(where))
        results_adjustment_out = self._cr.fetchall()
        # print("results_adjustment_out", results_adjustment_out)

        self._cr.execute(
            '''select sum(product_qty), product_id, product_uom 
            from stock_move move 
            where move.location_id NOT IN %s
            and move.location_dest_id IN %s
            and product_id IN %s and move.state = 'done' 
            and move.picking_id is null
            and move.inventory_id is null
            '''
            + (date_str and 'and ' + date_str + ' ' or '') + \
            '''
            group by product_id, product_uom''', tuple(where))
        results_production_in = self._cr.fetchall()
        # print("results_production_in", results_production_in)

        self._cr.execute(
            '''select sum(product_qty), product_id, product_uom 
            from stock_move move 
            where move.location_id IN %s
            and move.location_dest_id NOT IN %s
            and product_id IN %s and move.state = 'done' 
            and move.picking_id is null
            and move.inventory_id is null
            ''' + (date_str and 'and ' + date_str + ' ' or '') + \
            ''' group by product_id, product_uom''', tuple(where))
        results_production_out = self._cr.fetchall()
        # print("results_production_out", results_production_out)

        incoming_purchases, incoming_returns, outgoing, internal, adjustment, production = 0, 0, 0, 0, 0, 0
        # Count the quantities
        for quantity, prod_id, prod_uom in results_incoming_purchases:
            incoming_purchases += quantity
        for quantity, prod_id, prod_uom in results_incoming_returns:
            incoming_returns += quantity
        for quantity, prod_id, prod_uom in results_outgoing:
            outgoing += quantity
        for quantity, prod_id, prod_uom in results_internal_in:
            internal += quantity
        for quantity, prod_id, prod_uom in results_internal_out:
            internal -= quantity
        for quantity, prod_id, prod_uom in results_adjustment_in:
            adjustment += quantity
        for quantity, prod_id, prod_uom in results_adjustment_out:
            adjustment -= quantity
        for quantity, prod_id, prod_uom in results_production_in:
            production += quantity
        for quantity, prod_id, prod_uom in results_production_out:
            production -= quantity
        return {
            'incoming_purchases': incoming_purchases,
            'incoming_returns': incoming_returns,
            'outgoing': outgoing,
            'internal': internal,
            'adjustment': adjustment,
            'production': production,
            'balance': incoming_purchases + incoming_returns - outgoing + internal + adjustment + production
        }

    def act_getstockreport(self):
        temp_dir = tempfile.gettempdir() or '/tmp'
        f_name = os.path.join(temp_dir, 'stock_report.xlsx')
        workbook = xlsxwriter.Workbook(f_name)
        date_format = workbook.add_format({'num_format':'d-m-yyyy',
                                           'align': 'center',
                                           'valign': 'vcenter'})
        # Styles
        style_header = workbook.add_format({
            'bold': 1,
            'border': 1,
            'align': 'center',
            'valign': 'vcenter'})
        style_data = workbook.add_format({
            'border': 1,
            'align': 'left'})
        style_data2 = workbook.add_format({
            'border': 1,
            'align': 'center'})
        style_data3 = workbook.add_format({
            'border': 1,
            'align': 'right'})
        style_total = workbook.add_format({
            'bold': 1,
            'border': 1,
            'align': 'center',
            'valign': 'vcenter'})
        style_header2 = workbook.add_format({
            'bold': 1,
            'align': 'center',
            'valign': 'vcenter'})
        style_header.set_font_size(18)
        style_header.set_text_wrap()
        style_header.set_bg_color('#d7e4bd')
        style_header.set_font_name('Agency FB')
        style_header.set_border(style=2)
        style_data.set_font_size(12)
        style_data.set_text_wrap()
        style_data.set_font_name('Agency FB')
        style_data2.set_font_size(12)
        style_data2.set_font_name('Agency FB')
        style_data3.set_font_size(12)
        style_data3.set_font_name('Agency FB')
        style_total.set_font_size(12)
        style_total.set_text_wrap()
        style_total.set_border(style=2)
        # date_format.set_font_size(12)
        # date_format.set_bg_color('#d7e4bd')
        # date_format.set_font_name('Agency FB')
        # date_format.set_border(style=2)
        style_header2.set_font_size(12)
        style_header2.set_bg_color('#d7e4bd')
        style_header2.set_font_name('Agency FB')
        style_header2.set_border(style=2)
        worksheet = workbook.add_worksheet('Stock Report')
        worksheet.set_column(0, 0, 35)
        worksheet.set_column(1, 1, 35)
        worksheet.set_column(2, 2, 12)
        worksheet.set_column(3, 3, 12)
        worksheet.set_column(4, 4, 12)
        worksheet.set_column(5, 5, 12)
        worksheet.set_column(6, 6, 12)
        worksheet.set_column(7, 7, 12)
        worksheet.set_row(0, 25)

        product_obj = self.env['product.product']
        price_prec = self.env['decimal.precision'].precision_get('Product Price')
        # Getting locations to fetch report for
        locations = self.get_locations()
        locations = self.env['stock.location'].browse(list(set(locations.ids)))
        locations = locations.sorted(lambda l: l.level)
        products = self.product_ids
        # products = product_obj.browse([19, 85])
        if not products:
            products = product_obj.search([])
        row, col = 0, 0
        worksheet.merge_range(row, col + 1, row, col + 4, "Inventory Report", style_header)
        row += 1
        worksheet.write(row, col, 'Company', style_header2)
        worksheet.write(row + 1, col, self.company_id and self.company_id.name or 'ALL', style_data2)
        worksheet.write(row, col + 1, 'Warehouse', style_header2)
        warehouse_name = ''
        # if self.warehouse_ids:
        #     for w in self.warehouse_ids:
        #         warehouse_name = warehouse_name + w.name + ', '
        # else:
        #     warehouse_name = 'ALL'
        if self.warehouse_id:
            warehouse_name = warehouse_name + self.warehouse_id.name + ', '
        else:
            warehouse_name = 'ALL'
        worksheet.write(row + 1, col + 1, warehouse_name, style_data2)
        worksheet.write(row, col + 2, 'Date From', style_header2)
        if self.from_date:
            from_date = fields.Datetime.from_string(self.from_date)
            worksheet.write_datetime(row + 1, col + 2, from_date or ' ', date_format)
        worksheet.write(row, col + 3, 'Date To', style_header2)
        to_date = fields.Datetime.from_string(self.to_date)
        worksheet.write(row + 1, col + 3, to_date or ' ', date_format)
        worksheet.write(row, col + 4, ' ', style_header2)
        worksheet.write(row, col + 5, ' ', style_header2)
        worksheet.write(row, col + 6, ' ', style_header2)
        worksheet.write(row, col + 7, ' ', style_header2)
        worksheet.write(row, col + 8, ' ', style_header2)
        row += 2
        col = 0
        worksheet.write(row, col, 'Product', style_header2)
        worksheet.write(row, col + 1, 'Location', style_header2)
        worksheet.write(row, col + 2, 'Opening', style_header2)
        worksheet.write(row, col + 3, 'Purchased', style_header2)
        worksheet.write(row, col + 4, 'Returned', style_header2)
        worksheet.write(row, col + 5, 'Sales', style_header2)
        worksheet.write(row, col + 6, 'Internal', style_header2)
        worksheet.write(row, col + 7, 'Adjustment', style_header2)
        worksheet.write(row, col + 8, 'Production', style_header2)
        worksheet.write(row, col + 9, 'Closing', style_header2)
        if self.show_valuation:
            worksheet.write(row, col + 10, 'Valuation', style_header2)
        row += 1
        if self.from_date:
            print("from date +++++++++++++++++++++", self.from_date)
            from_date = fields.Datetime.from_string(self.from_date)
            my_datetime = datetime(from_date.year, from_date.month, from_date.day)
            # correct_date_time = my_datetime + timedelta(hours=2, minutes=30)
            previous_date = datetime.strptime(
                str(my_datetime), DEFAULT_SERVER_DATETIME_FORMAT) - timedelta(days=1)
            # correct_date_time = my_datetime + timedelta(hours=2, minutes=30)
            # previous_date = self.get_localised_date(previous_date)
            print("previous updae", previous_date)
        for product in products.sorted(lambda p: p.name):
            processed_loc_ids = []
            if self.report_by == 'location_wise':
                for location in locations:
                    if location.id in processed_loc_ids:
                        continue
                    child_locations = self.get_child_locations(location)
                    processed_loc_ids += child_locations.ids
                    col = 0
                    opening_dict = {}
                    if self.from_date:
                        opening_dict = self.get_product_available(product, False, previous_date,
                                                                  location)
                    inventory_dict = self.get_product_available(product, self.from_date, self.to_date,
                                                                location)
                    print(inventory_dict)
                    closing_balance = opening_dict.get('balance', 0.0) + inventory_dict.get('balance', 0.0)
                    if self.skip_zero_stock and \
                            float_is_zero(closing_balance, precision_digits=price_prec):
                        continue
                    worksheet.write(row, col, product.name_get()[0][1], style_data)
                    worksheet.write(row, col + 1, location.complete_name, style_data)
                    worksheet.write(row, col + 2, opening_dict.get('balance', 0.0), style_data3)
                    worksheet.write(row, col + 3, inventory_dict.get('incoming_purchases', 0.0), style_data3)
                    worksheet.write(row, col + 4, inventory_dict.get('incoming_returns', 0.0), style_data3)
                    worksheet.write(row, col + 5, inventory_dict.get('outgoing', 0.0), style_data3)
                    worksheet.write(row, col + 6, inventory_dict.get('internal', 0.0), style_data3)
                    worksheet.write(row, col + 7, inventory_dict.get('adjustment', 0.0), style_data3)
                    worksheet.write(row, col + 8, inventory_dict.get('production', 0.0), style_data3)
                    worksheet.write(row, col + 9, closing_balance, style_data3)
                    if self.show_valuation:
                        product_costing = round(closing_balance * product.standard_price, price_prec)
                        worksheet.write(row, col + 10, product_costing, style_data3)
                    row += 1
            else:
                col = 0
                opening_dict = {}
                if self.from_date:
                    opening_dict = self.get_product_available(product, False, previous_date,
                                                              locations)
                inventory_dict = self.get_product_available(product, self.from_date, self.to_date,
                                                            locations)
                print(inventory_dict)
                closing_balance = opening_dict.get('balance', 0.0) + inventory_dict.get('balance', 0.0)
                if self.skip_zero_stock and \
                        float_is_zero(closing_balance, precision_digits=price_prec):
                    continue
                worksheet.write(row, col, product.name_get()[0][1], style_data)
                worksheet.write(row, col + 1, ' ', style_data)
                worksheet.write(row, col + 2, opening_dict.get('balance', 0.0), style_data3)
                worksheet.write(row, col + 3, inventory_dict.get('incoming_purchases', 0.0), style_data3)
                worksheet.write(row, col + 4, inventory_dict.get('incoming_returns', 0.0), style_data3)
                worksheet.write(row, col + 5, inventory_dict.get('outgoing', 0.0), style_data3)
                worksheet.write(row, col + 6, inventory_dict.get('internal', 0.0), style_data3)
                worksheet.write(row, col + 7, inventory_dict.get('adjustment', 0.0), style_data3)
                worksheet.write(row, col + 8, inventory_dict.get('production', 0.0), style_data3)
                worksheet.write(row, col + 9, closing_balance, style_data3)
                if self.show_valuation:
                    product_costing = round(closing_balance * product.standard_price, price_prec)
                    worksheet.write(row, col + 10, product_costing, style_data3)
                row += 1
        # Writing Total Formula
        col = 0
        worksheet.merge_range(row, col, row, col + 1, "Total", style_total)
        col_length = 9
        if self.show_valuation:
            col_length += 1
        for col in range(2, col_length):
            amount_start = rowcol_to_cell(4, col)
            amount_stop = rowcol_to_cell(row - 1, col)
            formula = '=ROUND(SUM(%s:%s), 0)' % (amount_start, amount_stop)
            worksheet.write_formula(row, col, formula, style_total)
        row += 1
        workbook.close()
        f = open(f_name, 'rb')
        data = f.read()
        f.close()
        name = "%s.xlsx" % ("StockReport_" + str(self.from_date or '') + '_' + str(self.to_date or ''))
        out_wizard = self.env['xlsx.output'].create({'name': name,
                                                     'xls_output': base64.standard_b64encode(data)})
        view_id = self.env.ref('gts_stock_xlsx_report.xlsx_output_form').id
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'xlsx.output',
            'target': 'new',
            'view_mode': 'form',
            'res_id': out_wizard.id,
            'views': [[view_id, 'form']],
        }

    def get_opening_stock(self, moves_domain, all_locations, previous_date):
        moves_domain = [('company_id', '=', self.company_id.id), ('date', '<=', str(previous_date.date())),
                        ('product_id', '=', self.product_id.id), ('state', '=', 'done')]
        stocks = self.env['stock.move'].search(moves_domain, order='date asc')
        print('stocks...', stocks)
        print('moves_domain...', moves_domain)
        qty_on_hand = 0
        for move in stocks:
            col = 0
            if self.warehouse_id and move.warehouse_id and self.warehouse_id.id != move.warehouse_id.id:
                print('skiping Warehouse..id, reference...', move.id, move.origin)
                continue
            if move.location_id.id not in all_locations.ids and move.location_dest_id.id not in all_locations.ids:
                print('skiping Location..id, reference...', move.id, move.origin)
                continue
            col_count = 3
            quantity = move.product_uom_qty
            print('move.origin quantity....', move.id, move.origin, quantity)
            print('move.location....', move.location_id, move.location_dest_id)
            # Purchase
            if move.location_id.id not in all_locations.ids and move.location_dest_id.id in \
                    all_locations.ids and move.picking_id and not move.inventory_id and \
                    not move.origin_returned_move_id and move.picking_id.picking_type_code == 'incoming':
                col_count = 4
                qty_on_hand += move.product_uom_qty
                print('Purchase++++++++++')
            elif move.location_id.id in all_locations.ids and move.location_dest_id.id not in \
                    all_locations.ids and move.picking_id and not move.inventory_id and \
                    move.origin_returned_move_id and \
                    move.origin_returned_move_id.picking_id.picking_type_code == 'incoming' \
                    and move.picking_id.picking_type_code == 'outgoing':
                col_count = 5
                qty_on_hand -= move.product_uom_qty
                print('Purchase Return++++++++++')
            # Sales
            elif move.location_id.id in all_locations.ids and move.location_dest_id.id not in \
                    all_locations.ids and move.picking_id and not move.inventory_id and \
                    not move.origin_returned_move_id and move.picking_id.picking_type_code == 'outgoing':
                col_count = 6
                qty_on_hand -= move.product_uom_qty
                # print('Sales++++++++++')
            elif move.location_id.id not in all_locations.ids and move.location_dest_id.id in \
                    all_locations.ids and move.picking_id and not move.inventory_id and \
                    move.origin_returned_move_id and \
                    move.origin_returned_move_id.picking_id.picking_type_code == 'outgoing' \
                    and move.picking_id.picking_type_code == 'incoming':
                col_count = 7
                qty_on_hand += move.product_uom_qty
                # print('Sale Return++++++++++')
            # Internal Transfer
            elif self.warehouse_id and move.location_id.id not in all_locations.ids and move.location_dest_id.id in \
                    all_locations.ids and move.picking_id and not move.inventory_id and \
                    move.picking_id.picking_type_code == 'internal':
                col_count = 8
                quantity = move.product_uom_qty
                qty_on_hand += move.product_uom_qty
                # print('Internal 1 ++++++++++')
            elif self.warehouse_id and move.location_id.id in all_locations.ids and move.location_dest_id.id not in \
                    all_locations.ids and move.picking_id and not move.inventory_id and \
                    move.picking_id.picking_type_code == 'internal':
                col_count = 8
                quantity = - move.product_uom_qty
                qty_on_hand -= move.product_uom_qty
                # print('Internal 2++++++++++')
            elif not self.warehouse_id and move.location_id.id in all_locations.ids and move.location_dest_id.id in \
                    all_locations.ids and move.picking_id and not move.inventory_id and \
                    move.picking_id.picking_type_code == 'internal':
                col_count = 8
                # qty_on_hand -= move.product_uom_qty
                # print('Internal 3++++++++++')
            # elif not self.warehouse_id and move.location_id.id in all_locations.ids and move.location_dest_id.id not in \
            #          all_locations.ids and move.picking_id and not move.inventory_id and \
            #          move.picking_id.picking_type_code == 'internal':
            #     col_count = 8
            #     quantity = - quantity
            #     qty_on_hand += quantity
            # Adjustement
            elif move.location_id.id not in all_locations.ids and move.location_dest_id.id in \
                    all_locations.ids and not move.picking_id and move.inventory_id:
                col_count = 9
                qty_on_hand += move.product_uom_qty
                # print('Adjustment IN ++++++++++')
            elif move.location_id.id in all_locations.ids and move.location_dest_id.id not in \
                    all_locations.ids and not move.picking_id and move.inventory_id:
                col_count = 9
                quantity = - move.product_uom_qty
                qty_on_hand -= move.product_uom_qty
                # print('Adjustment OUT ++++++++++')
            # Production
            elif move.location_id.id not in all_locations.ids and move.location_dest_id.id in \
                    all_locations.ids and not move.picking_id and not move.inventory_id:
                col_count = 10
                qty_on_hand += move.product_uom_qty
                # print('Production IN ++++++++++')
            elif move.location_id.id in all_locations.ids and move.location_dest_id.id not in \
                    all_locations.ids and not move.picking_id and not move.inventory_id:
                col_count = 10
                quantity = - move.product_uom_qty
                qty_on_hand -= move.product_uom_qty
                # print('Production OUT ++++++++++')
            if col_count == 3:
                # print('move.origin...', move.origin)
                raise UserWarning(_('No Condition applied !'))
        return qty_on_hand

    def detailed_movement_report(self):
        to_date = fields.Datetime.from_string(self.to_date).date()
        end_date = datetime(to_date.year, to_date.month, to_date.day) + timedelta(hours=23, minutes=59, seconds=59)
        print("end DAte", end_date)
        temp_dir = tempfile.gettempdir() or '/tmp'
        f_name = os.path.join(temp_dir, 'stock_report.xlsx')
        workbook = xlsxwriter.Workbook(f_name)
        date_format = workbook.add_format({'num_format': 'd-m-yyyy',
                                           'align': 'center',
                                           'valign': 'vcenter'})
        # Styles
        style_header = workbook.add_format({
            'bold': 1,
            'border': 1,
            'align': 'center',
            'valign': 'vcenter'})
        style_data = workbook.add_format({
            'border': 1,
            'align': 'left'})
        style_data2 = workbook.add_format({
            'border': 1,
            'align': 'center'})
        style_data3 = workbook.add_format({
            'border': 1,
            'align': 'right'})
        style_total = workbook.add_format({
            'bold': 1,
            'border': 1,
            'align': 'center',
            'valign': 'vcenter'})
        style_header2 = workbook.add_format({
            'bold': 1,
            'align': 'center',
            'valign': 'vcenter'})
        style_header.set_font_size(18)
        style_header.set_text_wrap()
        style_header.set_bg_color('74F7B6') #('#d7e4bd')
        style_header.set_font_name('Agency FB')
        style_header.set_border(style=2)
        style_data.set_font_size(12)
        style_data.set_text_wrap()
        style_data.set_font_name('Agency FB')
        style_data2.set_font_size(12)
        style_data2.set_font_name('Agency FB')
        style_data3.set_font_size(12)
        style_data3.set_font_name('Agency FB')
        style_total.set_font_size(12)
        style_total.set_text_wrap()
        style_total.set_border(style=2)
        # date_format.set_font_size(12)
        # date_format.set_bg_color('#d7e4bd')
        date_format.set_font_name('Agency FB')
        date_format.set_border(style=1)
        style_header2.set_font_size(12)
        style_header2.set_bg_color('74F7B6') #('#d7e4bd')
        style_header2.set_font_name('Agency FB')
        style_header2.set_border(style=2)
        worksheet = workbook.add_worksheet('Stock Report')
        worksheet.set_column(0, 0, 20)
        worksheet.set_column(1, 1, 12)
        worksheet.set_column(2, 2, 20)
        worksheet.set_column(3, 3, 12)
        worksheet.set_column(4, 4, 12)
        worksheet.set_column(5, 5, 17)
        worksheet.set_column(6, 6, 12)
        worksheet.set_column(7, 7, 15)
        worksheet.set_column(8, 8, 17)
        worksheet.set_column(9, 9, 12)
        worksheet.set_column(10, 10, 17)
        worksheet.set_column(11, 11, 12)
        worksheet.set_column(12, 12, 12)
        worksheet.set_column(13, 13, 15)
        # worksheet.set_row(0, 25)
        row, col = 0, 0
        worksheet.merge_range(row, col + 1, row, col + 4, "Detailed Report", style_header)
        row += 1
        worksheet.write(row, col, 'Company', style_header2)
        worksheet.write(row + 1, col, self.company_id and self.company_id.name or 'ALL', style_data3)
        worksheet.write(row, col + 1, 'Product', style_header2)
        worksheet.write(row+1, col + 1, self.product_id.name, style_data3)
        worksheet.write(row, col + 2, 'Warehouse', style_header2)
        warehouse_name = ''
        if self.warehouse_id:
            warehouse_name = warehouse_name + self.warehouse_id.name + ', '
        else:
            warehouse_name = 'ALL'
        worksheet.write(row + 1, col + 2, warehouse_name, style_data3)
        worksheet.write(row, col + 3, 'Location', style_header2)
        if self.location_id:
            worksheet.write(row + 1, col + 3, self.location_id.location_id.name+'/'+self.location_id.name or ' ')
        worksheet.write(row, col + 4, 'Date From', style_header2)
        if self.from_date:
            from_date = fields.Datetime.from_string(self.from_date)
            worksheet.write_datetime(row + 1, col + 4, from_date or ' ', date_format)
        worksheet.write(row, col + 5, 'Date To', style_header2)
        to_date = fields.Datetime.from_string(self.to_date)
        worksheet.write(row + 1, col + 5, to_date or ' ', date_format)
        # worksheet.write(row, col + 5, ' ', style_header2)
        # worksheet.write(row, col + 6, ' ', style_header2)
        # worksheet.write(row, col + 7, ' ', style_header2)
        # worksheet.write(row, col + 8, ' ', style_header2)
        # worksheet.write(row, col + 9, ' ', style_header2)
        row += 2
        col = 0
        worksheet.write(row, col, 'Ref', style_header2)
        worksheet.write(row, col + 1, 'Date', style_header2)
        worksheet.write(row, col + 2, 'Name', style_header2)
        worksheet.write(row, col + 3, 'Opening', style_header2)
        worksheet.write(row, col + 4, 'Purchase', style_header2)
        worksheet.write(row, col + 5, 'Purchase Return', style_header2)
        worksheet.write(row, col + 6, 'Sales', style_header2)
        worksheet.write(row, col + 7, 'Sales Return', style_header2)
        worksheet.write(row, col + 8, 'Internal Transfer', style_header2)
        worksheet.write(row, col + 9, 'Adjustment', style_header2)
        worksheet.write(row, col + 10, 'Production/Others', style_header2)
        worksheet.write(row, col + 11, 'Value', style_header2)
        worksheet.write(row, col + 12, 'On Hand', style_header2)
        worksheet.write(row, col + 13, 'Average Cost', style_header2)
        if self.show_valuation:
            worksheet.write(row, col + 14, 'Valuation', style_header2)
        row += 1
        col = 0
        locations = self.get_locations()
        locations = self.env['stock.location'].browse(list(set(locations.ids)))
        locations = locations.sorted(lambda l: l.level)
        all_locations = self.get_child_locations(locations)
        print('all_locations...', all_locations)
        domain = [('company_id', '=', self.company_id.id), ('date', '<=', str(end_date.date())),
                  ('product_id', '=', self.product_id.id), ('state', '=', 'done')]
        # if self.warehouse_id:
        #     domain += [('warehouse_id', '=', self.warehouse_id.id)]
        qty_on_hand = 0
        if self.from_date:
            # print('from dayte', self.from_date)
            # previous_date = self.get_localised_date(self.from_date)
            from_date = fields.Datetime.from_string(self.from_date)
            my_datetime = datetime(from_date.year, from_date.month, from_date.day)
            print('my_datetime', my_datetime)
            previous_date = datetime.strptime(
                str(my_datetime), DEFAULT_SERVER_DATETIME_FORMAT) - timedelta(days=1)
            # correct_date_time = previous_date + timedelta(hours=3)
            # print('previous_date..', previous_date)
            # previous_date1 = self.get_localised_date(previous_date)
            print('previous_date..', previous_date)
            qty_available = self.get_opening_stock(domain, all_locations, previous_date)
            # print('qty_available...', qty_available)
            location = False
            if self.location_id:
                location = self.location_id
            elif self.warehouse_id:
                location = self.warehouse_id.lot_stock_id
            else:
                location = self.env['stock.location'].search([
                    ('usage', '=', 'internal'), '|', ('company_id', '=', self.company_id.id),
                    ('company_id', '=', False)], order='level asc')
            opening_dict = self.get_product_available(self.product_id, to_date=previous_date,
                                                      location=location)
            qty_available = opening_dict.get('balance', 0.0)
            # print('qty_available..2.', qty_available)
            qty_on_hand += qty_available
            worksheet.write(row, col, '', style_data3)
            worksheet.write(row, col + 1, from_date or ' ', date_format)
            worksheet.write(row, col + 2, 'Opening', style_data3)
            worksheet.write(row, col + 3, qty_available or 0, style_data3)
            worksheet.write(row, col + 4, '', style_data3)
            worksheet.write(row, col + 5, '', style_data3)
            worksheet.write(row, col + 6, '', style_data3)
            worksheet.write(row, col + 7, '', style_data3)
            worksheet.write(row, col + 8, '', style_data3)
            worksheet.write(row, col + 9, '', style_data3)
            worksheet.write(row, col + 10, '', style_data3)
            worksheet.write(row, col + 11, qty_available * self.product_id.standard_price or 0, style_data3)
            worksheet.write(row, col + 12, qty_available or 0, style_data3)
            worksheet.write(row, col + 13, self.product_id.standard_price or 0, style_data3)
            row += 1
            # domain += [('date', '>=', self.from_date)]
            domain += [('date', '>=', str(my_datetime.date()))]
        # print('domain...', domain)
        stocks = self.env['stock.move'].search(domain, order='date asc')
        # print('stocks...', stocks)
        for move in stocks:
            col = 0
            if self.warehouse_id and move.warehouse_id and self.warehouse_id.id != move.warehouse_id.id:
                # print('skiping Warehouse..id, reference...', move.id, move.origin)
                continue
            if move.location_id.id not in all_locations.ids and move.location_dest_id.id not in all_locations.ids:
                # print('skiping Location..id, reference...', move.id, move.origin)
                continue
            move_date = fields.Datetime.from_string(move.date)
            worksheet.write(row, col, move.origin, style_data3)
            worksheet.write(row, col + 1, move_date or ' ', date_format)
            worksheet.write(row, col + 2, move.name, style_data3)
            worksheet.write(row, col + 3, '', style_data3)
            worksheet.write(row, col + 4, '', style_data3)
            worksheet.write(row, col + 5, '', style_data3)
            worksheet.write(row, col + 6, '', style_data3)
            worksheet.write(row, col + 7, '', style_data3)
            worksheet.write(row, col + 8, '', style_data3)
            worksheet.write(row, col + 9, '', style_data3)
            worksheet.write(row, col + 10, '', style_data3)
            worksheet.write(row, col + 11, '', style_data3)
            worksheet.write(row, col + 12, '', style_data3)
            worksheet.write(row, col + 13, '', style_data3)
            col_count = 3
            quantity = move.product_uom_qty
            # print('move.origin quantity....', move.id, move.origin, quantity)
            # print('move.location....', move.location_id, move.location_dest_id)
            # Purchase
            if move.location_id.id not in all_locations.ids and move.location_dest_id.id in \
                    all_locations.ids and move.picking_id and not move.inventory_id and \
                    not move.origin_returned_move_id and move.picking_id.picking_type_code == 'incoming':
                col_count = 4
                qty_on_hand += move.product_uom_qty
                print('Purchase++++++++++')
            elif move.location_id.id in all_locations.ids and move.location_dest_id.id not in \
                    all_locations.ids and move.picking_id and not move.inventory_id and \
                    move.origin_returned_move_id and \
                    move.origin_returned_move_id.picking_id.picking_type_code == 'incoming' \
                    and move.picking_id.picking_type_code == 'outgoing':
                col_count = 5
                qty_on_hand -= move.product_uom_qty
                print('Purchase Return++++++++++')
            # Sales
            elif move.location_id.id in all_locations.ids and move.location_dest_id.id not in \
                    all_locations.ids and move.picking_id and not move.inventory_id and \
                    not move.origin_returned_move_id and move.picking_id.picking_type_code == 'outgoing':
                col_count = 6
                qty_on_hand -= move.product_uom_qty
                print('Sales++++++++++')
            elif move.location_id.id not in all_locations.ids and move.location_dest_id.id in \
                    all_locations.ids and move.picking_id and not move.inventory_id and \
                    move.origin_returned_move_id and \
                    move.origin_returned_move_id.picking_id.picking_type_code == 'outgoing' \
                    and move.picking_id.picking_type_code == 'incoming':
                col_count = 7
                qty_on_hand += move.product_uom_qty
                print('Sale Return++++++++++')
            # Internal Transfer
            elif self.warehouse_id and move.location_id.id not in all_locations.ids and move.location_dest_id.id in \
                    all_locations.ids and move.picking_id and not move.inventory_id and \
                    move.picking_id.picking_type_code == 'internal':
                col_count = 8
                quantity = move.product_uom_qty
                qty_on_hand += move.product_uom_qty
                print('Internal 1 ++++++++++')
            elif self.warehouse_id and move.location_id.id in all_locations.ids and move.location_dest_id.id not in \
                    all_locations.ids and move.picking_id and not move.inventory_id and \
                    move.picking_id.picking_type_code == 'internal':
                col_count = 8
                quantity = - move.product_uom_qty
                qty_on_hand -= move.product_uom_qty
                print('Internal 2++++++++++')
            elif not self.warehouse_id and move.location_id.id in all_locations.ids and move.location_dest_id.id in \
                    all_locations.ids and move.picking_id and not move.inventory_id and \
                    move.picking_id.picking_type_code == 'internal':
                col_count = 8
                # qty_on_hand -= move.product_uom_qty
                print('Internal 3++++++++++')
            # elif not self.warehouse_id and move.location_id.id in all_locations.ids and move.location_dest_id.id not in \
            #          all_locations.ids and move.picking_id and not move.inventory_id and \
            #          move.picking_id.picking_type_code == 'internal':
            #     col_count = 8
            #     quantity = - quantity
            #     qty_on_hand += quantity
            # Adjustement
            elif move.location_id.id not in all_locations.ids and move.location_dest_id.id in \
                    all_locations.ids and not move.picking_id and move.inventory_id:
                col_count = 9
                qty_on_hand += move.product_uom_qty
                print('Adjustment IN ++++++++++')
            elif move.location_id.id in all_locations.ids and move.location_dest_id.id not in \
                    all_locations.ids and not move.picking_id and move.inventory_id:
                col_count = 9
                quantity = - move.product_uom_qty
                qty_on_hand -= move.product_uom_qty
                print('Adjustment OUT ++++++++++')
            # Production
            elif move.location_id.id not in all_locations.ids and move.location_dest_id.id in \
                    all_locations.ids and not move.picking_id and not move.inventory_id:
                col_count = 10
                qty_on_hand += move.product_uom_qty
                print('Production IN ++++++++++')
            elif move.location_id.id in all_locations.ids and move.location_dest_id.id not in \
                    all_locations.ids and not move.picking_id and not move.inventory_id:
                col_count = 10
                quantity = - move.product_uom_qty
                qty_on_hand -= move.product_uom_qty
                print('Production OUT ++++++++++')
            if col_count == 3:
                print('move.origin...', move.origin)
                raise UserWarning(_('No Condition applied !'))
            worksheet.write(row, col + col_count, quantity or 0, style_data3)
            worksheet.write(row, col + 11, qty_on_hand * self.product_id.standard_price or 0, style_data3)
            worksheet.write(row, col + 12, qty_on_hand or 0, style_data3)
            worksheet.write(row, col + 13, self.product_id.standard_price or 0, style_data3)
            row += 1
            print('quantity.qty_on_hand..', quantity, qty_on_hand)
        workbook.close()
        f = open(f_name, 'rb')
        data = f.read()
        f.close()
        name = "%s.xlsx" % ("StockReport_" + str(self.from_date or '') + '_' + str(self.to_date or ''))
        out_wizard = self.env['xlsx.output'].create({'name': name,
                                                     'xls_output': base64.standard_b64encode(data)})
        view_id = self.env.ref('gts_stock_xlsx_report.xlsx_output_form').id
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'xlsx.output',
            'target': 'new',
            'view_mode': 'form',
            'res_id': out_wizard.id,
            'views': [[view_id, 'form']],
        }

    def get_localised_date(self, dt, days=0, return_datetime=True):
        ''' Function return next localized date based on days passed from source.
        -1 for yesterday, +1 for tomorrow, 0 for today '''
        print("dt++++++++++++++++++++++===============+++++++++++++++++", dt)
        # Timezone conversion
        user = self.env['res.users'].browse(self._uid)
        tz = False
        if user.tz:
            tz = pytz.timezone(user.tz)
        else:
            tz = pytz.timezone('Etc/GMT+3') or pytz.utc
        # tradeDay = day.trade_date + timedelta(hours=6)
        # td1 = pytz.timezone("Europe/London").localize(tradeDay, is_dst=None)
        # tradeDay = td1.astimezone(pytz.utc)
        # Finding next date(Localized) based on days passed
        next_date = dt + timedelta(days=days)
        next_date = pytz.utc.localize(next_date, is_dst=None)
        next_date = datetime.strptime(next_date.astimezone(tz).strftime(
            DEFAULT_SERVER_DATETIME_FORMAT), DEFAULT_SERVER_DATETIME_FORMAT)
        print("12222222222222222222222222222222222", next_date)
        if return_datetime:
            return next_date
        return next_date.strftime(DEFAULT_SERVER_DATE_FORMAT)
