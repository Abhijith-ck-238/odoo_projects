from odoo import models, fields, api


class HospitalPatient(models.Model):
    _name = 'hospital.patient'
    _description = 'Hospital Patient'
    _rec_name = 'name'

    name = fields.Char(string='Patient Name', required=True)
    patient_code = fields.Char(string='Patient Code')
    ward_id = fields.Many2one('hospital.ward', string='Ward')

    display_name = fields.Char(
        compute='_compute_display_name',
        store=False,
    )

    @api.depends('name', 'patient_code', 'ward_id')
    def _compute_display_name(self):
        for record in self:
            name = record.name or ''
            if record.patient_code:
                name = f'[{record.patient_code}] {name}'
            if record.ward_id:
                name = f'{name} ({record.ward_id.display_name})'
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
                 ('patient_code', operator, name),
                 ('name', operator, name)] + domain,
                limit=limit
            )
            return records.name_get()
        return super().name_search(
            name=name, domain=domain, operator=operator, limit=limit
        )
