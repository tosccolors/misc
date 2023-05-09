# -*- coding: utf-8 -*-
# Copyright 2018 TOSC ((www.tosc.nl).)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields, api, _
from datetime import datetime, timedelta
from odoo.exceptions import ValidationError
from dateutil.relativedelta import relativedelta

class Lead(models.Model):
    _inherit = "crm.lead"

    date_action = fields.Datetime('Next Activity Date', index=True)
    internal_note = fields.Boolean('Internal Note')