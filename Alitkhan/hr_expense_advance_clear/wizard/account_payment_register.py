# Copyright 2020 Ecosoft Co., Ltd (https://ecosoft.co.th/)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)

from odoo import _, models
from odoo.exceptions import UserError
from odoo.tools import float_compare
from markupsafe import Markup
from odoo import api


class AccountPaymentRegister(models.TransientModel):
    _inherit = "account.payment.register"

    def _validate_over_return(self):
        """Actual remaining = amount to clear - clear pending
        and it is not legit to return more than remaining"""
        clearings = (
            self.env["hr.expense.sheet"]
            .browse(self.env.context.get("clearing_sheet_ids", []))
            .filtered(lambda sheet: sheet.state == "approve")
        )
        amount_not_clear = sum(clearings.mapped("total_amount"))
        actual_remaining = self.source_amount_currency - amount_not_clear
        more_info = ""
        symbol = self.source_currency_id.symbol
        if amount_not_clear:
            more_info = _("\nNote: pending amount clearing is %(symbol)s%(amount)s") % {
                "symbol": symbol,
                "amount": f"{amount_not_clear:,.2f}",
            }
        if float_compare(self.amount, actual_remaining, 2) == 1:
            raise UserError(
                _(
                    "You cannot return advance more than actual remaining "
                    "(%(symbol)s%(amount)s)%(more_info)s"
                )
                % {
                    "symbol": symbol,
                    "amount": f"{actual_remaining:,.2f}",
                    "more_info": more_info,
                }
            )
        else:
            sheet = self.env["hr.expense.sheet"].browse(self.env.context.get("active_id", []))
            sheet.write({"clearing_residual": sheet.clearing_residual - self.amount})

    def _init_payments(self, to_process, edit_mode=False):
        if self.env.context.get("hr_return_advance"):
            self._validate_over_return()
            active_ids = self.env.context.get("active_ids", [])
            if self.env.context.get("active_model") == "account.move":
                lines = self.env["account.move"].browse(active_ids).line_ids
            elif self.env.context.get("active_model") == "account.move.line":
                lines = self.env["account.move.line"].browse(active_ids)

            expense_sheet = lines.expense_id.sheet_id
            for x in to_process:
                x["create_vals"]["partner_type"] = "customer"
                x["create_vals"]["advance_id"] = expense_sheet.id

        payments = super()._init_payments(to_process, edit_mode)
        return payments


    def _create_payments(self):
        """Update the payment state when the clearing amount exceeds the advance."""
        payments = super()._create_payments()
        if self.env.context.get("expense_clearing"):
            for payment in payments:
                payment.write({"move_id": payment.move_id.id, "state": "paid"})
                sheet = self.env["hr.expense.sheet"].browse(self.env.context.get("active_id", []))
                if sheet:
                    sheet.write({'state': 'done'})

                    payment_link = Markup(
                        '<a href="#" data-oe-model="account.payment" data-oe-id="%s">%s</a>'
                    ) % (payment.id, payment.name)

                    message_body = Markup('Expense cleared with payment of %s%s extra on %s.Reference: %s') % (
                        payment.currency_id.symbol,
                        '{:,.2f}'.format(payment.amount),
                        payment.date,
                        payment_link
                    )

                    sheet.message_post(
                        body=message_body,
                        subject="Expense Cleared",
                        message_type='notification',
                        subtype_xmlid='mail.mt_note'
                    )
        return payments

class AccountPayment(models.Model):
    _inherit = "account.payment"

    @api.model
    def _get_valid_payment_account_types(self):
        res = super()._get_valid_payment_account_types()
        # If we are in the clearing context, we want to allow the advance account
        # but only if it doesn't cause a conflict with a standard payable line.
        if self._context.get('expense_clearing') or self._context.get('hr_return_advance'):
            emp_advance = self.env.ref('hr_expense_advance_clear.product_emp_advance', False)
            if emp_advance and emp_advance.property_account_expense_id:
                advance_type = emp_advance.property_account_expense_id.account_type
                
                # Check for standard payable/receivable lines in the active moves
                has_standard_payable = False
                active_model = self._context.get('active_model')
                active_ids = self._context.get('active_ids', [])
                
                if active_model == 'account.move':
                    moves = self.env['account.move'].browse(active_ids)
                    has_standard_payable = any(
                        l.account_type in res and not l.reconciled 
                        for l in moves.line_ids
                    )
                elif active_model == 'account.move.line':
                    lines = self.env['account.move.line'].browse(active_ids)
                    has_standard_payable = any(
                        l.account_type in res and not l.reconciled 
                        for l in lines
                    )

                # If there's a real payable (like the extra $10), Odoo should only see that.
                # If we add advance_type here, the wizard will see two types and crash.
                if not has_standard_payable and advance_type not in res:
                    if isinstance(res, tuple):
                        res = res + (advance_type,)
                    else:
                        res.append(advance_type)
        return res
