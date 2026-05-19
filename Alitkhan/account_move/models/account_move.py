from odoo import models


class AccountMove(models.Model):
    _inherit = 'account.move'

    def action_link_purchase_order(self):
        return {
            'name': "Link PO",
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'link.purchase',
            'view_id': self.env.ref('account_move.link_purchase_wizard_view').id,
            'target': 'new',
            'context': {'default_bill_id': self.id},
        }
