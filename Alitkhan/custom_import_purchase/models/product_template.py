from odoo import models


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    def action_activate_tracking(self):
        for rec in self:
            rec.tracking = "lot"