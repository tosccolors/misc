# -*- coding: utf-8 -*-
# Copyright (C) 2021 - Today: Magnus (http://www.magnus.nl)
# @author: Vincent Verheul (v.verheul@magnus.nl)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


from odoo import api, fields, models


class BiSQLView(models.Model):
    _inherit = 'bi.sql.view'

    show_on_dashboard = fields.Boolean(
        string='On Dashboard',
        copy=True,
        default=True,
        help="Show a menu item for this query on the dashboard")

    
    def button_create_ui(self):
        self.tree_view_id = self.env['ir.ui.view'].create(
            self._prepare_tree_view()).id
        self.graph_view_id = self.env['ir.ui.view'].create(
            self._prepare_graph_view()).id
        self.pivot_view_id = self.env['ir.ui.view'].create(
            self._prepare_pivot_view()).id
        self.search_view_id = self.env['ir.ui.view'].create(
            self._prepare_search_view()).id
        self.action_id = self.env['ir.actions.act_window'].create(
            self._prepare_action()).id
        # creation of menu item is now made conditional
        if self.show_on_dashboard:
            self.menu_id = self.env['ir.ui.menu'].create(
                self._prepare_menu()).id
        self.write({'state': 'ui_valid'})
