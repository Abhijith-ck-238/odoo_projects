from odoo import fields, models


class TrainingType(models.Model):
    _name = "training.type"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = "Training Type"

    name = fields.Char(string="Name")
    allowed_stage_ids = fields.Many2many('training.stage', string="Allowed Stages")
    require_letters_certificate = fields.Boolean(string= "Require Letters & Certificates")
    activity_users_ids = fields.Many2many('res.users', string="Users for Activity")

