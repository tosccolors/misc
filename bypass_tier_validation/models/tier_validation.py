# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)
from odoo import _, api, fields, models


class TierValidation(models.AbstractModel):
    _inherit = "tier.validation"

    def _check_allow_write_under_validation(self, vals):
        """Allow to add exceptions for fields that are allowed to be written
        even when the record is under validation."""

        if self.env.user.has_group('bypass_tier_validation.group_bypass_tier_validation'):
            return True
        return super()._check_allow_write_under_validation(vals)

    def _check_state_conditions(self, vals):
        """
        Always allow group_bypass_tier_validation
        """
        if self.env.user.has_group('bypass_tier_validation.group_bypass_tier_validation'):
            return False
        return super()._check_state_conditions(vals)

    def _notify_accepted_reviews_body(self):
        """
        Add the name of the review that was accepted to body
        """
        reviews = self.review_ids.filtered(lambda x: x.done_by == self.env.user and x.status == 'approved')
        if reviews:
            return (
                _('Review %s was accepted') % ', '.join(reviews.mapped('name'))
            ) + ((
                '(%s)' % ', '.join(filter(None, reviews.mapped('comment')))
            ) if list(filter(None, reviews.mapped('comment'))) else '')
        else:
            return super()._notify_accepted_reviews_body()
