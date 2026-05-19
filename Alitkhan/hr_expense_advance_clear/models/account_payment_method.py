# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, models

class AccountPaymentMethodLine(models.Model):
    _inherit = 'account.payment.method.line'

    @api.model
    def name_search(self, name='', args=None, operator='ilike', limit=100):
        args = args or []
        domain = ['|', ('name', operator, name), ('journal_id', operator, name)]
        records = self.search(domain + args, limit=limit)
        return [(rec.id, rec.display_name) for rec in records]
