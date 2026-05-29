from odoo import fields, models

class LetterStages(models.Model):
    _name = 'letter.stage'
    _description = 'Letter Stages'
    _order = 'sequence'

    name = fields.Char(required=True, translate=True)
    sequence = fields.Integer()
    move_from_user_ids = fields.Many2many('res.users', string="Move from User",
                                          relation="rel_move_from_user_letter_stage")
    move_to_user_ids = fields.Many2many('res.users', string="Move to User",
                                        relation="rel_move_to_user_letter_stage")
    send_activity_for_modality_manager = fields.Boolean(string="Send Activity for Modality Manager")
    require_approval_letter = fields.Boolean(string="Require Approval Letter")
