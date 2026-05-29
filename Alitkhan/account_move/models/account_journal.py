# -*- coding: utf-8 -*-
from odoo import models


class AccountJournal(models.Model):
    _inherit = 'account.journal'

    def open_action(self):
        if self.type in ('bank', 'cash', 'credit') and not self._context.get(
                'action_name'):
            self.ensure_one()
            # Get the default action dictionary
            action = self.env[
                'account.bank.statement.line']._action_open_bank_reconciliation_widget(
                extra_domain=[],
                default_context={
                    'default_journal_id': self.id,
                    'search_default_journal_id': self.id,
                },
            )
            # Odoo hardcodes [('state', '!=', 'cancel')] into the domain.
            # We override it to an empty list so ALL records show up immediately.
            action['domain'] = []
            return action

        return super().open_action()

    def _fill_bank_cash_dashboard_data(self, dashboard_data):
        """ Override to compute reconcile and to check counts including draft entries. """
        super()._fill_bank_cash_dashboard_data(dashboard_data)

        bank_cash_journals = self.filtered(
            lambda journal: journal.type in ('bank', 'cash', 'credit'))
        if not bank_cash_journals:
            return

        # Query counts with state != 'cancel' to match the bank reconciliation widget
        self._cr.execute("""
            SELECT st_line.journal_id,
                   COUNT(st_line.id)
              FROM account_bank_statement_line st_line
              JOIN account_move st_line_move ON st_line_move.id = st_line.move_id
             WHERE st_line.journal_id IN %s
               AND st_line.company_id IN %s
               AND NOT st_line.is_reconciled
               AND st_line_move.checked IS TRUE
               AND st_line_move.state != 'cancel'
          GROUP BY st_line.journal_id
        """, [tuple(bank_cash_journals.ids), tuple(self.env.companies.ids)])
        number_to_reconcile = {
            journal_id: count
            for journal_id, count in self.env.cr.fetchall()
        }

        to_check = {
            journal: (amount, count)
            for journal, amount, count in
            self.env['account.bank.statement.line']._read_group(
                domain=[
                    ('journal_id', 'in', bank_cash_journals.ids),
                    ('move_id.company_id', 'in', self.env.companies.ids),
                    ('move_id.checked', '=', False),
                    ('move_id.state', '!=', 'cancel'),
                ],
                groupby=['journal_id'],
                aggregates=['amount:sum', '__count'],
            )
        }

        for journal in bank_cash_journals:
            currency = journal.currency_id or self.env['res.currency'].browse(
                journal.company_id.sudo().currency_id.id)
            to_check_balance, number_to_check = to_check.get(journal, (0, 0))
            dashboard_data[journal.id].update({
                'number_to_reconcile': number_to_reconcile.get(journal.id, 0),
                'number_to_check': number_to_check,
                'to_check_balance': currency.format(to_check_balance),
            })