from odoo import models, fields


class AccountPayment(models.Model):
    _inherit = 'account.payment'

    expense_sheet_id = fields.Many2many('hr.expense.sheet',
                                       string="Expense Report", store=True)

    # def action_assign_expense_report(self):
    #     expense_sheet_ids = self.env['hr.expense.sheet'].search(
    #         [('account_move_ids', '!=', False), ('state', '=', 'done'),
    #          ('is_sheet_checked', '!=', True)], limit=3500)
    #     for exp in expense_sheet_ids:
    #         exp.account_move_ids.expense_sheet_id = exp.id
    #         move_line_ids = exp.account_move_ids.mapped('line_ids')
    #         for line in move_line_ids:
    #             reconciled_ids = line._reconciled_lines()
    #             move_lines = self.env['account.move.line'].search(
    #                 [('id', 'in', reconciled_ids)])
    #             for r_line in move_lines:
    #                 if not r_line.payment_id:
    #                     payments = self.env['account.payment'].search(
    #                         [('move_line_ids', 'in', r_line.id)])
    #                     if payments:
    #                         r_line.payment_id = payments.id
    #                         if not r_line.payment_id.expense_sheet_id:
    #                             r_line.payment_id.expense_sheet_id = [(4, exp.id)]
    #                 else:
    #                     r_line.sudo().payment_id.sudo().expense_sheet_id = [(4, exp.id)]
    #         exp.sudo().is_sheet_checked = True
