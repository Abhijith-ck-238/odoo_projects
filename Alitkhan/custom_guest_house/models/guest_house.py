from odoo import models, fields


class Guesthouse(models.Model):
    _name = 'guest.house'
    _description = 'Guest House'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string="Guest House Name")
    province_id = fields.Many2one('contract.province', 'Province')
    bed_ids = fields.One2many('guest.house.bed', 'guest_house_id')
    total_bed = fields.Integer("Total Beds", compute="compute_total_bed")
    available_bed = fields.Integer("Available Beds", compute="compute_available_bed")
    color = fields.Integer()
    active = fields.Boolean(default=True)
    user_ids = fields.Many2many('res.users', string="Users Notified")

    def compute_total_bed(self):
        for rec in self:
            rec.total_bed = self.env['guest.house.bed'].search_count([('guest_house_id', '=', rec.id)])
    def compute_available_bed(self):
        for rec in self:
            rec.available_bed = self.env['guest.house.bed'].search_count([('guest_house_id', '=', rec.id), ('reserve', '=', False)])
