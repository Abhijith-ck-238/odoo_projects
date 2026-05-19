from odoo import fields, models


class TrainingType(models.Model):
    _name = "training.location"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = "Training Location"

    name = fields.Char(string="Name")
