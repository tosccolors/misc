from odoo import SUPERUSER_ID, api

def post_init_hook(cr, registry):
    env = api.Environment(cr, SUPERUSER_ID, {})
    AccountMove = env['account.move']
    for message in env['mail.message'].search([
        ('model', '=', 'account.move'),
        ('tracking_value_ids.field.name', '=', 'is_move_sent'),
        ('tracking_value_ids.new_value_integer', '=', 1),
    ]):
        move = AccountMove.browse(message.res_id)
        if move.is_move_sent:
            move.sent_date = message.create_date
