from odoo import fields, models


class FieldAccess(models.Model):
    _name = 'field.access'
    _description = 'Field Access'

    field_id = fields.Many2one('ir.model.fields', string="Fields", domain=lambda self: [(
                                  'model_id', '=', self.env.ref(
                                      'pledge_assets.model_pledge_pledge').id)])
    user_ids = fields.Many2many('res.users', string="Users")
