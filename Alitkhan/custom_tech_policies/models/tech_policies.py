from odoo import fields, models, api, _


class TechPolicies(models.Model):
    _name = 'tech.policies'
    _description = "Tech Policies"

    name = fields.Char(string="Decision")
    sequence = fields.Char(string="Sequence", readonly=True, copy=False, default="New")
    date = fields.Char(string="Date")
    authorized_person = fields.Char(string="Authorized Person")
    example = fields.Char(string="Example")
    notes = fields.Char(string="Note")

    @api.model
    def create(self, vals):
        if vals.get('sequence', _('New')) == _('New'):
            vals['sequence'] = self.env['ir.sequence'].next_by_code(
                'tech.policies.seq') or _('New')
        return super(TechPolicies, self).create(vals)
