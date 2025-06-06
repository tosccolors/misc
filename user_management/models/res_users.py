# -*- coding: utf-8 -*-

from odoo import models, fields, api
from lxml import etree
import json

class Users(models.Model):
    _inherit = 'res.users'

    @api.depends('groups_id')
    def _compute_group(self):
        for obj in self:
            obj.is_user_management_group = self.env.user.has_group("user_management.group_user_management")

    is_user_management_group = fields.Boolean(compute=_compute_group, default=False, string='Is User Management Group?')



    # @api.model
    # def get_view(self, view_id=None, view_type='form', **options):
    #     result = super(Users, self).get_view(view_id, view_type, **options)
    #     print ('------------usermanagement', view_type)
    #     if view_type == "form":
    #         # import pdb; pdb.set_trace();
    #         view = etree.XML(result["arch"])
    #         page = view.find(".//page[@name='access_rights']/group[0]")
    #         if page is not None:
    #             import pdb;
    #             pdb.set_trace();
    #             page.attrib["invisible"]= "1"
    #             # modifiers = json.loads(page.get("modifiers", {}))
    #             # modifiers.update(
    #             #     {
    #             #         "invisible": True,
    #             #     }
    #             # )
    #             # page.set("modifiers", json.dumps(modifiers))
    #         result["arch"] = etree.tostring(view)
        # if (self.user_has_groups(
        #         "hr.group_hr_manager,hr.group_hr_user") or SUPERUSER_ID == self._uid) and view_type == 'tree':
        #     doc = etree.XML(result['arch'])
        #     pro_nodes = doc.xpath("//field[@name='project_id']")
        #     if pro_nodes:
        #         # pro_nodes[0].set('widget', 'many2one_clickable')
        #         # setup_modifiers(
        #         #     pro_nodes[0], result['fields']['project_id'])
        #         pro_nodes[0].attrib["widget"] = "many2one_clickable"
        #     tsk_nodes = doc.xpath("//field[@name='task_id']")
        #     if tsk_nodes:
        #         # tsk_nodes[0].set('widget', 'many2one_clickable')
        #         # setup_modifiers(
        #         #     tsk_nodes[0], result['fields']['task_id'])
        #         tsk_nodes[0].attrib["widget"] = "many2one_clickable"
        #     result['arch'] = etree.tostring(doc)
        # return result

    # def fields_view_get(
    #     self, view_id=None, view_type="form", toolbar=False, submenu=False
    # ):
    #     result = super().fields_view_get(
    #         view_id=view_id, view_type=view_type, toolbar=toolbar, submenu=submenu
    #     )
    #     print ('------------1111',)
    #     doc = etree.XML(res["arch"])
    #     if view_type == 'form':
    #
    #
    #         for node in doc.xpath("//page[@name='access_rights']"):
    #             node.set("invisible", "1")
    #             modifiers = json.loads(node.get("modifiers"))
    #             node.set("modifiers", json.dumps(modifiers))
    #
    #     result['arch'] = etree.tostring(doc, encoding='unicode')
    #         # page = doc.xpath("//page[@name='access_rights']")
    #         # if page:
    #         #     page[0].set("invisible", "1")
    #         #     page.set("invisible", "1")
    #         #     modifiers = json.loads(page.get("modifiers"))
    #         #     modifiers.update(
    #         #         {
    #         #             "column_invisible": False,
    #         #         }
    #         #     )
    #         #     field.set("modifiers", json.dumps(modifiers))
    #         # res["arch"] = etree.tostring(
    #         #     view,
    #         #     encoding="unicode",
    #         # ).replace("\t", "")
    #     return result