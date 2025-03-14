from odoo import api, models


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    @api.model_create_multi
    def create(self, vals_list):
        """
        Poison the cache so that moves look like not having an OU.
        This makes super not force all move line OUs to the move's OU
        Still do what super does if there is no OU and we're self balanced
        """
        moves = self.env['account.move']

        for vals in vals_list:
            for move in moves.browse(vals.get('move_id', [])):
                moves |= move
                if move.company_id.ou_is_self_balanced and not vals.get('operating_unit_id'):
                    vals['operating_unit_id'] = move.operating_unit_id.id

        for move in moves:
            move._cache['operating_unit_id'] = None

        result = super().create(vals_list)

        moves.invalidate_cache(fnames=['operating_unit_id'], ids=moves.ids)
        return result

    def _create_exchange_difference_move(self):
        """
        Make sure exchange difference move has self's OU set
        """
        self = self.with_context(default_operating_unit_id=self.operating_unit_id[:1].id)
        return super()._create_exchange_difference_move()
