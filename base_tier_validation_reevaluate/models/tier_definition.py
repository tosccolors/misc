from odoo import models


class TierDefinition(models.Model):
    _inherit = 'tier.definition'


    def _reevaluate_pending_reviews(self):
        reviews = self.env['tier.review'].search([
            ('definition_id', 'in', self.ids),
            ('status', '=', 'pending'),
        ])
        records_by_model = {}
        for review in reviews:
            Model = self.env[review.model]
            records_by_model.setdefault(review.model, Model)
            records_by_model[review.model] |= Model.browse(review.res_id)

        reviews.unlink()
        for records in records_by_model.values():
            records.request_validation()
