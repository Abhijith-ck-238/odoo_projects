from odoo import fields, models


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    shipment_type_id = fields.Many2one('shipment.type', string="Shipment Type")

    def write(self, vals):
        if vals.get('account_id') == False:
            vals['account_id'] = self.account_id.id
        return super(AccountMoveLine, self).write(vals)