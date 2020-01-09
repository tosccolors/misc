# Copyright 2016-2018 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

import logging

from odoo import models

_logger = logging.getLogger(__name__)


class JiraBackend(models.Model):
    _name = 'jira.backend'
    # Commented as the inherited model (server.env.mixin) is not available anywhere in the code
    # _inherit = ["jira.backend", "server.env.mixin"]
    _inherit = ["jira.backend"]

    @property
    def _server_env_fields(self):
        return {
            "uri": {},
            "verify_ssl": {},
            "odoo_webhook_base_url": {},
        }
