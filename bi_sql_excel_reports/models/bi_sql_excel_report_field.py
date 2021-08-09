# -*- coding: utf-8 -*-
# Copyright (C) 2021 - Today: Magnus (http://www.magnus.nl)
# @author: Vincent Verheul (v.verheul@magnus.nl)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


from odoo import fields, models


class BiSqlExcelReportField(models.Model):
    _name = 'bi.sql.excel.report.field'
    _order = 'report_id, sequence'

    report_id = fields.Many2one(
        comodel_name='bi.sql.excel.report',
        string='Report',
        copy=True,
        index=True,
        ondelete='cascade')

    report_is_index = fields.Boolean(
        string='Rpt Select index',
        related='report_id.is_select_index')

    sequence = fields.Integer(
        string='Sequence',
        required=True,
        help="Determines the sequence of the fields")

    name = fields.Char(
        string='Field name',
        required=True,
        help="Field (technical) name of the underlying query / view")

    formula = fields.Char(
        string='Pivot formula',
        help="Excel pivot formula (instead of a selected field)")

    pivot_area = fields.Selection(
        selection=[
            ('n/a', 'N/A'),
            ('filter', 'Filter'),
            ('columns', 'Columns - Legend'),
            ('rows', 'Rows - Axis'),
            ('values', 'Values'),
            ('slicer', 'Slicer'),
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
