# -*- coding: utf-8 -*-
from odoo import models, fields, api


class AccountJournal(models.Model):
    _inherit = 'account.journal'

    custom_user_ids = fields.Many2many(
        'res.users',
        string='Allow Access Users',
        copy=True,
    )


    # TODO: Commented due to access issue in opening vendor and customer payments.
    # @api.model
    # def _search(self, args, offset=0, limit=None, order=None):
    #     user = self.env.user
    #     journal_group = self.env.ref(
    #         'invoice_by_journal_users.group_limited_acces_journal_user',
    #         raise_if_not_found=False)
    #
    #     # Ensure group exists and the current user is in the restricted group
    #     if journal_group and user in journal_group.users:
    #         # args+=[('custom_user_ids', 'in', self.env.user.ids)]
    #         args.append('|')
    #         args.append(('custom_user_ids', '=',
    #                      False))  # Allow access if no users are defined
    #         args.append(('custom_user_ids', 'in', [
    #             user.id]))  # Allow access if the user is explicitly listed
    #
    #     return super()._search(args, offset, limit, order)
