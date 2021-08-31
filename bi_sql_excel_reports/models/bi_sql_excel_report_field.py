# -*- coding: utf-8 -*-
# Copyright (C) 2021 - Today: Magnus (http://www.magnus.nl)
# @author: Vincent Verheul (v.verheul@magnus.nl)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


from odoo import api, fields, models


class BiSqlExcelReportField(models.Model):
    _name = 'bi.sql.excel.report.field'
    _order = 'report_id, sequence'

    @api.model
    def _get_default_is_select_index(self):
        return self.env.context.get('parent_report_is_select_index', False)

    @api.model
    def _get_default_sequence(self):  # only works on records saved to the database ..
        new_seq = 1
        report_id = self.env.context.get('parent_report_id', False)
        existing = self.search([])  # 'report_id', '=', report_id
        existing = [rec for rec in existing if rec.report_id.id == report_id]
        if existing:
            new_seq = max([rec.sequence for rec in existing]) + 1
        return new_seq

    @api.model
    def _get_query_id(self):
        if self.report_id:
            report_query_id = self.report_id.query
        else:
            report_query_id = self.env.context.get('parent_report_query_id', False)
        return report_query_id

    report_id = fields.Many2one(
        comodel_name='bi.sql.excel.report',
        string='Report',
        copy=True,
        index=True,
        ondelete='cascade',
        help="Reference to the report object")

    report_query_id = fields.Many2one(
        string='Rpt Query ID',
        copy=True,
        readonly=True,
        related='report_id.query',
        default=_get_query_id,
        help="Reference to the report SQL View ID")

    report_is_index = fields.Boolean(
        string='Rpt Select index',
        copy=True,
        related='report_id.is_select_index',
        default=_get_default_is_select_index,
        help="Reference to the report field is_select_index")

    sequence = fields.Integer(
        string='Sequence',
        required=True,
        default=_get_default_sequence,
        help="Determines the sequence of the fields")

    name_id = fields.Many2one(
        comodel_name='bi.sql.view.field',
        string='Field name',
        required=True,
        help="Field (technical) name (id) of the underlying query / view")

    name = fields.Char(
        related='name_id.name',
        string='Field txt',
        readonly=True,
        store=True,
        help="Field (technical) name")

    formula = fields.Char(
        string='Pivot formula',
        help="Excel pivot formula (instead of a selected field)")

    pivot_area = fields.Selection(
        selection=[
            ('n/a', 'N/A'),
            ('filter', 'Filter'),
            ('slicer', 'Slicer'),
            ('columns', 'Columns or Legend'),
            ('rows', 'Rows or Axis'),
            ('values:sum', 'Values:Sum'),
            ('values:count', 'Values:Count'),
            ('values:average', 'Values:Average'),
            ('values:max', 'Values:Max'),
            ('values:min', 'Values:Min'),
            ('values:product', 'Values:Product'),
            ('values:count_numbers', 'Values:Count Numbers'),
            ('values:stdev', 'Values:StDev'),
            ('values:stdevp', 'Values:StDevp'),
            ('values:var', 'Values:Var'),
            ('values:varp', 'Values:Varp'),
        ],
        string='Pivot area',
        default='n/a',
        required=True,
        help="Pivot area for tables or charts")

    caption = fields.Char(
        string='Caption',
        help="Field name (caption) as shown in Excel, overrides the default (technical) field name")

    format = fields.Char(
        string='Number format',
        help="Excel field format for numerical fields, for example  0  for no decimals")

    subtotal = fields.Boolean(
        string='Sub total',
        default=False,
        help="Calculate sub total for this field in the pivot table")

    show_details = fields.Boolean(
        string='Show details',
        default=True,
        help="Show details on the next hierarchy level in a pivot table")

    is_user = fields.Boolean(
        string='Is user field',
        default=False,
        help="This field holds the username: used to filter on only user's records")

    filter_value = fields.Char(
        string='Filter value',
        help="Set this value to be the (initial) filter in Excel")

    global_filter = fields.Char(
        string='Global filter',
        help="Enter index (short name) from which a selection is required, for example: Projects")

    slicer_top = fields.Integer(
        string='Slicer top',
        help="Slicer top position in points")

    slicer_height = fields.Integer(
        string='Slicer height',
        help="Slicer height in points")

    index_info = fields.Boolean(
        string='Index Info',
        default=False,
        help="The field is displayed as an information field on an index page")

    index_field_width = fields.Integer(
        string='Index Width',
        default=25,
        help="The width (in points) of a field on an index page")
