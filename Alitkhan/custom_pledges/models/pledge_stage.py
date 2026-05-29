from odoo import fields, models


class PledgeStage(models.Model):
    _name = 'pledge.stage'
    _description = "Pledge Stage"

    name = fields.Char(string='Stage')
    sequence = fields.Integer(string='Sequence')
    move_from_user_ids = fields.Many2many('res.users', string="Move from User", relation="rel_move_from_user_pledge_stage")
    move_to_user_ids = fields.Many2many('res.users', string="Move to User", relation="rel_move_to_user_pledge_stage")
    is_from_user_notified = fields.Boolean(string="Notification for Move From User")
    is_to_user_notified = fields.Boolean(string="Notification for Move To User")
    other_users_notified = fields.Many2many('res.users', string="Other Users tobe Notified")
