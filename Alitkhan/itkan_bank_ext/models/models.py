# -*- coding: utf-8 -*-

from odoo import models, fields, api


class ResPartnerBankExt(models.Model):
    _inherit="res.partner.bank"

    swift=fields.Char(string="Swift Code")


class AccountBankStatementLine(models.Model):
    _inherit = 'account.bank.statement.line'

    def _seek_for_lines(self):
        """ Override to enforce singletons for liquidity_lines and suspense_lines.
        When custom imports or scripts create multiple bank lines in the same move,
        the bank.rec.widget crashes because it expects exactly one liquidity line
        and one suspense line per statement line.
        """
        liquidity_lines, suspense_lines, other_lines = super()._seek_for_lines()

        if len(liquidity_lines) > 1:
            other_lines += liquidity_lines[1:]
            liquidity_lines = liquidity_lines[0]

        if len(suspense_lines) > 1:
            other_lines += suspense_lines[1:]
            suspense_lines = suspense_lines[0]

        return liquidity_lines, suspense_lines, other_lines
