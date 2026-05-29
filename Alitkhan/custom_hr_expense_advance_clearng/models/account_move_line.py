from importlib.resources import _

from odoo import api, models
from odoo.exceptions import UserError


class AccountMove(models.Model):
    _inherit = 'account.move.line'

    # TODO: The below content is commented because it is not required in the latest database.The related functionality is no longer part of the current business process.Kept only for reference during migration and validation.



    # @api.constrains('account_id', 'display_type')
    # def _check_payable_receivable(self):
    #     for line in self:
    #         # Skip check if this is an employee advance operation
    #         if line.move_id.journal_id.type == 'purchase':
    #             continue  # Skip this constraint
    #
    #         account_type = line.account_id.account_type
    #         if line.move_id.is_sale_document(include_receipts=True):
    #             if account_type == 'liability_payable':
    #                 raise UserError(_("Account %s is of payable type, but is used in a sale operation.", line.account_id.code))
    #             if (line.display_type == 'payment_term') ^ (account_type == 'asset_receivable'):
    #                 raise UserError(_("Any journal item on a receivable account must have a due date and vice versa."))
    #         if line.move_id.is_purchase_document(include_receipts=True):
    #             if account_type == 'asset_receivable':
    #                 raise UserError(_("Account %s is of receivable type, but is used in a purchase operation.", line.account_id.code))
    #             if (line.display_type == 'payment_term') ^ (account_type == 'liability_payable'):
    #                 raise UserError(_("Any journal item on a payable account must have a due date and vice versa."))
