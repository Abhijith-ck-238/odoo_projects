# -*- coding: utf-8 -*-
from odoo import api, fields, models


class HelpdeskTicket(models.Model):
    _inherit = 'helpdesk.ticket'

    def write(self, vals):
        """Updating the method to get the live update of date_start and date_end
        field in this record in the corresponding fields in field service"""
        res = super().write(vals)
        for rec in self:
            if vals.get('date_start') or vals.get("date_end"):
                if rec.field_service_id:
                    updates = {}
                    if 'date_start' in vals:
                        updates['planned_date_begin'] = rec.date_start
                    if 'date_end' in vals:
                        updates['date_deadline'] = rec.date_end
                    if updates:
                        rec.field_service_id.write(updates)
        return res


class HrExpense(models.Model):
    _inherit = "hr.expense"


    is_cron_worked = fields.Boolean()


    def correcting_invoice_lines(self):
        for expense in self:
            moves = expense.sheet_id.account_move_ids
            if not moves:
                continue
            if moves.statement_id:
                continue

            company_currency = expense.company_currency_id
            # due_dates = {line.id: line.date_maturity for line in moves.line_ids}

            self.env.cr.execute("""
                UPDATE account_move_line
                SET currency_id = %s,
                    amount_currency = debit - credit
                WHERE move_id IN %s
                  AND expense_id = %s
            """, (company_currency.id, tuple(moves.ids), expense.id))
            self.env.cr.execute("""
                UPDATE account_move_line
                SET price_unit = debit / NULLIF(quantity, 0),
                    price_subtotal = debit,
                    price_total = debit
                WHERE move_id IN %s
                  AND expense_id = %s
                  AND display_type = 'product'
            """, (tuple(moves.ids), expense.id))
            print("Updated price_unit/subtotal/total via SQL for expense", expense.id)

            self.env.cr.execute("""
                UPDATE account_move_line aml
                SET amount_residual = aml.debit - aml.credit,
                    amount_residual_currency = aml.amount_currency
                WHERE aml.move_id IN %s
                  AND aml.expense_id = %s
            """, (tuple(moves.ids), expense.id))
            self.env.cr.execute("""
                UPDATE account_move am
                SET amount_residual = sub.total_residual,
                    amount_residual_signed = sub.total_residual
                FROM (
                    SELECT 
                        aml.move_id,
                        SUM(aml.amount_residual) AS total_residual
                    FROM account_move_line aml
                    WHERE aml.move_id IN %s
                    GROUP BY aml.move_id
                ) sub
                WHERE am.id = sub.move_id
            """, (tuple(moves.ids),))
            for rec in moves:
                sign = -1 if rec.move_type in ('in_invoice', 'out_refund') else 1

                new_total_in_currency = sum(line.price_total for line in rec.line_ids) * sign
                new_untaxed_in_currency = sum(line.price_subtotal for line in rec.line_ids) * sign
                self.env.cr.execute("""
                                          UPDATE account_move
                                          SET
                                              amount_total_in_currency_signed = %s,
                                              amount_untaxed_in_currency_signed = %s
                                          WHERE id = %s
                                      """, (new_total_in_currency, new_untaxed_in_currency, rec.id))
                rec.invalidate_recordset([
                    'amount_total_in_currency_signed',
                    'amount_untaxed_in_currency_signed'
                ])
            self.env.invalidate_all()

    @api.model
    def cron_fix_expense_price_unit(self):

        domain = [
            ('is_cron_worked', '=', False),
            ('date', '<=', '2026-01-15'),
            ('state', '!=', 'draft')]
        expenses = self.search(domain, limit=500, order='id')
        print("expenses", expenses)
        for expense in expenses:
            if expense.analytic_account_id and not expense.analytic_account_id.exists():
                continue
            expense.correcting_invoice_lines()
            expense.is_cron_worked = True

