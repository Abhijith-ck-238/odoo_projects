from odoo import fields, models

class TrainingStages(models.Model):
    _name = 'training.stage'
    _description = 'Training Stages'
    _order = 'sequence'

    name = fields.Char(required=True, translate=True)
    sequence = fields.Integer()
    require_letters_certificate = fields.Boolean(
        string="Require Letters & Certificates")
    move_from_user_ids = fields.Many2many('res.users', string="Move from User",
                                          relation="rel_move_from_user_training_stage")
    move_to_user_ids = fields.Many2many('res.users', string="Move to User",
                                        relation="rel_move_to_user_training_stage")
    require_purchase_order = fields.Boolean(string="Require Purchase Order")
    users_notified_po = fields.Many2many('res.users',string="Users Notified on PO Creation", relation='rel_users_notified_po_training_stage')
