# -*- coding: utf-8 -*-
##############################################################################
#
#    This module uses OpenERP, Open Source Management Solution Framework.
#    Copyright (C):
#        2016 Magnus Red www.magnus.nl
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>
#
##############################################################################



from odoo import api, fields, models, _, SUPERUSER_ID

class MassObject(models.Model):
    _inherit = "mass.editing"

    # Overridden:
    @api.multi
    def create_action(self):
        self.ensure_one()
        cr = self._cr
        vals = {}
        action_obj = self.env['ir.actions.act_window']

        cr.execute("""SELECT res_id FROM ir_model_data WHERE module=%s AND name in %s""",
                   ("mass_editing_auth", ('me_normal_user','group_mass_editing')))
        grp_ids = cr.fetchall()

        src_obj = self.model_id.model
        button_name = _('Mass Editing (%s)') % self.name
        vals['ref_ir_act_window_id'] = action_obj.create({
            'name': button_name,
            'type': 'ir.actions.act_window',
            'res_model': 'mass.editing.wizard',
            'src_model': src_obj,
            'view_type': 'form',
            'context': "{'mass_editing_object' : %d}" % (self.id),
            'view_mode': 'form, tree',
            'target': 'new',
            'groups_id': [(6, 0, grp_ids)],
        }).id
        # We make sudo as any user with rights in this model should be able
        # to create the action, not only admin
        vals['ref_ir_value_id'] = self.env['ir.values'].sudo().create({
            'name': button_name,
            'model': src_obj,
            'key2': 'client_action_multi',
            'value': "ir.actions.act_window," +
                     str(vals['ref_ir_act_window_id']),
        }).id
        self.write(vals)
        return True



# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
