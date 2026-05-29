from odoo import models, fields, api


class HospitalWard(models.Model):
    _name = 'hospital.ward'
    _description = 'Hospital Ward'
    _rec_name = 'name'

    name = fields.Char(string='Ward Name', required=True)
    code = fields.Char(string='Ward Code')
    capacity = fields.Integer(string='Capacity')

    display_name = fields.Char(
        compute='_compute_display_name',
        store=False,
    )

    @api.depends('name', 'code', 'capacity')
    def _compute_display_name(self):
        for record in self:
            name = record.name or ''
            if record.code:
                name = f'[{record.code}] {name}'
            if record.capacity:
                name = f'{name} (Cap: {record.capacity})'
            record.display_name = name

    def name_get(self):
        """Keep for backward compatibility."""
        return [(record.id, record.display_name) for record in self]

    @api.model
    def name_search(self, name='', domain=None, operator='ilike', limit=100):
        """Sync search with customized display. In Odoo 19, use domain instead of args."""
        domain = domain or []
        if name:
            records = self.search(
                ['|',
                 ('code', operator, name),
                 ('name', operator, name)] + domain,
                limit=limit
            )
            return records.name_get()
        return super().name_search(
            name=name, domain=domain, operator=operator, limit=limit
        )
