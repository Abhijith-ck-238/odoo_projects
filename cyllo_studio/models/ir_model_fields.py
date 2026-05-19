from odoo import api, models, fields


class IrModel(models.Model):
    _inherit = 'ir.model.fields'

    is_studio = fields.Boolean(string='Studio Field', default=False,
                               help="Notify field created through Studio")

    @api.model
    def create_new_fields(self, args):
        model = self.env['ir.model'].search([('model', '=', args['model'])])
        technical_name = 'x_cy_' + args['technical_name']
        ir_model_field = self.create({
            'name': technical_name,
            'complete_name': args['label'],
            'model': args['model'],
            'model_id': model.id,
            'ttype': args['field_type'],
            'field_description': args['help'],
            'state': 'manual',
            'is_studio': True
        })


class IrUiView(models.Model):
    _inherit = 'ir.ui.view'

    is_studio = fields.Boolean(string='Studio Field', default=False,
                               help="Notify field created through Studio")
