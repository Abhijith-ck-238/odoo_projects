# -*- coding: utf-8 -*-
""" HR Payroll Multi Currency """

from odoo import api, fields, models


class HrPayslip(models.Model):
    _inherit = 'hr.payslip'
    """
    HR Payroll Multi-Currency
    allow generate journal entry based on it
    """

    def _get_currency_amount(self, currency_from, currency_to, company_id,
                             amount, date=False):
        """

        :param currency_from: many2one
        :param currency_to: many2one
        :param company_id: many2one
        :param amount: float
        :param date: date
        :return: float
        """
        return currency_from._convert(amount,
                                      currency_to,
                                      company_id,
                                      date or fields.Date.today())

    def action_payslip_done(self):
        print('payslip done.......')
        res = super(HrPayslip, self).action_payslip_done()

        # Identify payslips not linked to a batch
        payslips_without_run = self.filtered(
            lambda slip: not slip.payslip_run_id)
        payslip_runs = (self - payslips_without_run).mapped('payslip_run_id')

        # Add other payslips from runs that are ready
        for run in payslip_runs:
            if run._are_payslips_ready():
                payslips_without_run |= run.slip_ids

        # Only update done payslips that have accounting entries (moves)
        payslips_to_update = payslips_without_run.filtered(
            lambda slip: slip.state == 'done' and slip.move_id
        )

        for slip in payslips_to_update:
            journal_currency = slip.journal_id.currency_id
            company_currency = slip.journal_id.company_id.currency_id

            # Skip if no multi-currency case
            if not journal_currency or journal_currency == company_currency:
                continue

            # Update move lines with converted amounts
            move = slip.move_id
            if not move:
                continue

            for line in move.line_ids:
                original_debit = line.debit
                original_credit = line.credit
                base_amount = original_debit if original_debit > 0 else original_credit

                converted_amount = self._get_currency_amount(
                    currency_from=journal_currency,
                    currency_to=company_currency,
                    company_id=slip.journal_id.company_id,
                    amount=base_amount,
                    date=move.date,
                )

                line.with_context(check_move_validity=False).write({
                    'debit': converted_amount if original_debit > 0 else 0.0,
                    'credit': converted_amount if original_credit > 0 else 0.0,
                    'amount_currency': original_debit if original_debit > 0 else -original_credit,
                    'currency_id': journal_currency.id,
                })

        return res

    def _get_payslip_currency(self):
        for rec in self:
            if rec.struct_id.journal_id.currency_id:
                rec.currency_id = rec.struct_id.journal_id.currency_id
            else:
                rec.currency_id = rec.struct_id.journal_id.company_id.currency_id

    currency_id = fields.Many2one(
        comodel_name='res.currency',
        readonly=True,
        compute="_get_payslip_currency",
        related="",
    )
    