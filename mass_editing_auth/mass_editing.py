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

from openerp.osv import orm, fields, osv
from openerp.tools.translate import _


from openerp import SUPERUSER_ID



class mass_object(orm.Model):
    _inherit = "mass.object"

    _columns = {
    }


    def create_action(self, cr, uid, ids, context=None):
        vals = {}
        action_obj = self.pool.get('ir.actions.act_window')
        ir_values_obj = self.pool.get('ir.values')

        cr.execute("""SELECT res_id FROM ir_model_data WHERE module=%s AND name in %s""",
                   ("mass_editing_auth", ('me_normal_user','group_mass_editing')))
        grp_ids = cr.fetchall()

        for data in self.browse(cr, uid, ids, context=context):
            src_obj = data.model_id.model
            button_name = _('Mass Editing (%s)') % data.name
            vals['ref_ir_act_window'] = action_obj.create(cr, SUPERUSER_ID, {
                'name': button_name,
                'type': 'ir.actions.act_window',
                'res_model': 'mass.editing.wizard',
                'src_model': src_obj,
                'view_type': 'form',
                'context': "{'mass_editing_object' : %d}" % (data.id),
                'view_mode': 'form,tree',
                'target': 'new',
                'auto_refresh': 1,
                'groups_id': [(6, 0, grp_ids)],
            }, context)
            vals['ref_ir_value'] = ir_values_obj.create(cr, uid, {
                'name': button_name,
                'model': src_obj,
                'key2': 'client_action_multi',
                'value': (
                    "ir.actions.act_window,%s" % vals['ref_ir_act_window']),
                'object': True,
            }, context)
        self.write(cr, uid, ids, {
            'ref_ir_act_window': vals.get('ref_ir_act_window', False),
            'ref_ir_value': vals.get('ref_ir_value', False),
        }, context)
        return True



mass_object()
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
