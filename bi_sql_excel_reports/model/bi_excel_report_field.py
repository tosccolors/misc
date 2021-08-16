# -*- coding: utf-8 -*-
# Copyright (C) 2021 - Today: Magnus (http://www.magnus.nl)
# @author: Vincent Verheul (v.verheul@magnus.nl)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


from odoo import fields, models


class BiExcelReportField(models.Model):
    _name = 'bi.excel.report.field'

    active = fields.Boolean('Active', default=True)

    report_id = fields.Many2one(
        comodel_name='bi.excel.report',
        string='Report',
        copy=True,
        index=True,
        ondelete='cascade')

    report_is_index = fields.Boolean(
        string='Is index',
        related='report_id.is_index')

    sequence = fields.Integer(
        string='Sequence',
        help="Determines the sequence of the fields")

    name = fields.Char(
        string='Field name',
        help="Field (technical) name of the underlying query / view")

    formula = fields.Char(
        string='Pivot formula',
        help="Excel pivot formula (instead of a selected field)")

    pivot_area = fields.Selection(
        selection=[
            ('n/a', 'N/A'),
            ('filter', 'Filter'),
            ('columns', 'Columns / Legend / Series'),
            ('rows', 'Rows / Axis / Categories'),
            ('values', 'Values'),
            ('slicer', 'Slicer'),
            ('timeline', 'Timeline')
        ],
        string='Pivot area',
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
        help="This field holds the username")

    filter_value = fields.Char(
        string='Filter value',
        help="Set this value to be the (initial) filter")

    slicer_top = fields.Integer(
        string='Slicer top',
        help="Slicer top position in points")

    slicer_height = fields.Integer(
        string='Slicer height',
        help="Slicer height in points")

    index_level = fields.Integer(
        string="Index Level",
        default=0,
        help="Hierarchy index level on an index page (-1 for hidden id column, 0 when not relevant)")

    index_info = fields.Boolean(
        string='Index Info',
        default=False,
        help="The field is displayed as an information field on an index page")
