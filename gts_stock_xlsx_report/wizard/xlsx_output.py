
from odoo import models, fields, api, _


class XlsxOutput(models.TransientModel):
    _name = 'xlsx.output'
    _description = "XLSX Report Download"

    name = fields.Char('Name')
    xls_output = fields.Binary('Download', readonly=True)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
