from werkzeug.urls import url_encode
from odoo import models, api, fields, _
from odoo.exceptions import UserError
from odoo.tools.safe_eval import safe_eval
# from odoo.addons.hr_expense.wizard.hr_expense_sheet_register_payment import HrExpenseSheetRegisterPaymentWizard
from odoo.addons.hr_expense.wizard.account_payment_register import \
    AccountPaymentRegister
from odoo.addons.hr_expense_advance_clearing.models.hr_expense_sheet import \
    HrExpenseSheet
from collections import defaultdict

# class HrExpenseSheetMpatch(HrExpenseSheet):
# class HrExpenseSheet(models.Model):
#     _inherit = "hr.expense.sheet"

# TODO: The below content is commented because it is not required in the latest database.The related functionality is no longer part of the current business process.Kept only for reference during migration and validation.

#
# def action_sheet_move_post(self):
#
#     res = super(HrExpenseSheet,self).action_sheet_move_post()
#     # Reconcile advance of this sheet with the advance_sheet
#     emp_advance = self.env.ref(
#         "hr_expense_advance_clearing.product_emp_advance")
#     for sheet in self:
#         move_lines = (
#                 sheet.account_move_ids.line_ids
#                 | sheet.advance_sheet_id.account_move_ids.line_ids
#         )
#         account_id = emp_advance.property_account_expense_id.id
#         adv_move_lines = (
#             self.env["account.move.line"]
#             .sudo()
#             .search([("id", "in", move_lines.ids),
#                      ("account_id", "=", account_id)])
#         )
#     return res
# HrExpenseSheet.action_sheet_move_post = action_sheet_move_post

# class HrExpenseSheetRegisterPaymentWizardMpatch(AccountPaymentRegister):
# class AccountPaymentRegister(models.TransientModel):
#     _inherit = 'account.payment.register'
#
# TODO: The below content is commented because it is not required in the latest database.The related functionality is no longer part of the current business process.Kept only for reference during migration and validation.

# def expense_post_payment(self):
#     self.ensure_one()
#     company = self.company_id
#     self = self.with_context(force_company=company.id,
#                              company_id=company.id)
#     context = dict(self._context or {})
#     active_ids = context.get('active_ids', [])
#     expense_sheet = self.env['hr.expense.sheet'].browse(active_ids)
#
#     # Create payment and post it
#     payment = self.env['account.payment'].create(self._get_payment_vals())
#     payment.expense_sheet_id = self._context.get('active_id')
#     payment.post()
#     # Log the payment in the chatter
#     body = (
#             _("A payment of %s %s with the reference <a href='/mail/view?%s'>%s</a> related to your expense %s has been made.") % (
#         payment.amount, payment.currency_id.symbol,
#         url_encode({'model': 'account.payment', 'res_id': payment.id}),
#         payment.name, expense_sheet.name))
#     expense_sheet.message_post(body=body)
#
#     # Reconcile the payment and the expense, i.e. lookup on the payable account move lines
#     account_move_lines_to_reconcile = self._prepare_lines_to_reconcile(
#         payment.move_line_ids + expense_sheet.account_move_ids.line_ids)
#     account_move_lines_to_reconcile.reconcile()
#
#     return {'type': 'ir.actions.act_window_close'}
#
# AccountPaymentRegister.expense_post_payment = expense_post_payment


class HrExpenseSheetExtend(models.Model):
    _inherit = 'hr.expense.sheet'

    clearng_amount = fields.Float(string="clearng amount", default=0,
                                  store=True)
    # remaining_budget = fields.Float(string="Remaining budget",
    #                                 # compute='_compute_remaining_budget',
    #                                 related='analytic_account_id.remaining_budget_amount',
    #                                 readonly=True)

    budget_reponsibles = fields.Many2many('res.users',
                                          relation="expense_budget_reponsible_rel",
                                          column1="expense_sheet_id",
                                          column2="budget_user",
                                          compute="compute_budget_responsible",
                                          string='Budget Responsible',
                                          store=True)

    is_sheet_checked = fields.Boolean()

    # # @api.depends('analytic_account_id')
    # def _compute_remaining_budget(self):
    #     for rec in self:
    #         rec.remaining_budget = 0
    #         if rec.analytic_account_id.id:
    #             print("rec.analytic_account_id.", rec.analytic_account_id)
    #             val = rec.analytic_account_id.remaining_budget_amount
    #             budget_amount = sum(self.env["budget.line"].search([
    #                 ("auto_account_id", "=", rec.analytic_account_id.id),
    #             ]).mapped("budget_amount"))
    #             analytic_lines = self.env["account.analytic.line"].search([("auto_account_id", "in", [rec.analytic_account_id.id])])
    #             tot_amount = 0
    #             total_exp = 0
    #             total = 0
    #             tot_amount =  budget_amount
    #             for line in analytic_lines:
    #                 total = total + round(line.amount, 2)
    #                 product_id = self.env.ref("hr_expense_advance_clearing.product_emp_advance")
    #                 if line.product_id.id == product_id.id:
    #                     amt = abs(round(line.amount, 2))
    #                     if line.x_studio_residual < amt or line.x_studio_residual == 0:
    #                         total_exp = total_exp + line.amount
    #
    #             rem = abs(round(total, 2)) - abs(round(total_exp, 2))
    #             total = round(tot_amount, 2) - round(rem, 2)
    #             rec.remaining_budget = total

    # TODO: The below content is commented because it is not required in the latest database.The related functionality is no longer part of the current business process.Kept only for reference during migration and validation.

    # def refuse_sheet(self, reason):
    #     # this function is copied from the original refuse_sheet() and edited
    #     # @M-Saeb
    #     if not self.env.user.has_groups(
    #             'hr_expense.group_hr_expense_team_approver'):
    #         raise UserError(
    #             _("Only Managers and HR Officers can approve expenses"))
    #
    #     self.write({'state': 'cancel'})
    #     for sheet in self:
    #         sheet.message_post_with_view(
    #             'hr_expense.hr_expense_template_refuse_reason',
    #             values={'reason': reason, 'is_sheet': True, 'name': self.name})
    #     self.activity_update()
    #
    #     for line in self.approval_lines:
    #         line.approved = False
    #         line.approved_date = False
    #     self.activity_unlink(['hr_expense.mail_act_expense_approval'],
    #                          user_id=self.next_approval_user.id)

    # TODO: The below content is commented because it is not required in the latest database.The related functionality is no longer part of the current business process.Kept only for reference during migration and validation.

    # @api.depends('analytic_account_id')
    # def compute_budget_responsible(self):
    #     for rec in self:
    #         rec.remaining_budget = 0
    #         if rec.analytic_account_id.budget_line_ids:
    #             for budget_line in rec.analytic_account_id.budget_line_ids:
    #                 if budget_line:
    #                     rec.budget_reponsibles = [
    #                         (4, budget_line.crossovered_budget_id.user_id.id)]
    #                 else:
    #                     rec.budget_reponsibles = []
    #
    #         else:
    #             rec.budget_reponsibles = []

    # TODO: The below content is commented because it is not required in the latest database.The related functionality is no longer part of the current business process.Kept only for reference during migration and validation.


    # def check_remaining_budget(self):
    #     """Check if any amount in t the lines is greater than the remaining
    #         amount in that analytic account in the analytic_distribution"""
    #     analytic_totals = defaultdict(float)
    #     for expense in self.expense_line_ids:
    #         if expense.analytic_distribution and expense.total_amount:
    #             for analytic_account_id, percentage in expense.analytic_distribution.items():
    #                 amount = expense.total_amount * (percentage / 100)
    #                 analytic_totals[analytic_account_id] += amount
    #     result = dict(analytic_totals)
    #     for analytic_account_id, total in result.items():
    #         analytic_account = self.env["account.analytic.account"].browse(
    #             int(analytic_account_id))
    #         remaining_amount = analytic_account.remaining_budget_amount
    #         if round(remaining_amount, 2) < total:
    #             return {"is_restrict": True, "an_account": analytic_account}
    #     return {"is_restrict": False}



    # def action_sheet_move_post(self):
    #     """
    #             override action_sheet_move_post to add condition to check whether the
    #             remaining budget amount less than the total amount on Expenses and raise
    #             a warning if the amount is less than total budget amount. Also added
    #             condition to check whether the remaining budget amount less than 20% of
    #             total budget amount and send notification to discuss channel if condition
    #             met.
    #             """


    # def _check_can_create_move(self):
    #     if self.analytic_account_id:
    #         tot_amount = sum(self.analytic_account_id.budget_line_ids.mapped(
    #             "budget_amount"))
    #         if self.advance_sheet_id:
    #             res = super(HrExpenseSheetExtend,
    #                         self)._check_can_create_move()
    #
    #             # Assign expense sheet ID to related account moves
    #             for move in self.account_move_ids:
    #                 move.expense_sheet_id = self.id
    #
    #             # Reconcile advances
    #             emp_advance = self.env.ref(
    #                 "hr_expense_advance_clearing.product_emp_advance")
    #
    #             for sheet in self:
    #                 move_lines = sheet.account_move_ids.mapped(
    #                     "line_ids") + sheet.advance_sheet_id.account_move_ids.mapped(
    #                     "line_ids")
    #                 account_id = emp_advance.property_account_expense_id.id
    #
    #                 adv_move_lines = self.env[
    #                     "account.move.line"].sudo().search([
    #                     ("id", "in", move_lines.ids),
    #                     ("account_id", "=", account_id)
    #                 ])
    #
    #                 # Perform reconciliation
    #                 unreconciled_lines = adv_move_lines.filtered(
    #                     lambda l: not l.reconciled)
    #                 if unreconciled_lines:
    #                     unreconciled_lines.reconcile()
    #
    #             return res
    #
    #         else:
    #             if self.remaining_budget <= (
    #                     tot_amount * 0.2):
    #                 channel_ref = 'custom_hr_expense_advance_clearng.technical_budget_reminder_channel' \
    #                     if self.employee_id.new_divisions.name == 'Technical' \
    #                     else 'custom_hr_expense_advance_clearng.general_budget_reminder_channel'
    #
    #                 channel_id = self.env.ref(channel_ref)
    #                 user_id = self.env.user.partner_id.id
    #
    #                 for emp_user in self.budget_reponsibles:
    #                     emp_user_id = emp_user.partner_id
    #                     notification_ids = [(0, 0, {
    #                         'res_partner_id': emp_user_id.id,
    #                         'notification_type': 'inbox'
    #                     })]
    #
    #                     message = _(
    #                         "The <a href=# data-oe-model=account.analytic.account data-oe-id=%d>%s</a> "
    #                         "holds less than 20%% (%s) set on "
    #                         "<a href=# data-oe-model=hr.expense.sheet data-oe-id=%d>%s</a>."
    #                     ) % (
    #                                   self.analytic_account_id.id,
    #                                   self.analytic_account_id.name,
    #                                   round(
    #                                       self.analytic_account_id.sudo().remaining_budget_amount,
    #                                       2),
    #                                   self.id,
    #                                   self.name
    #                               )
    #
    #                     channel_id.message_post(
    #                         author_id=user_id,
    #                         body=message,
    #                         message_type='notification',
    #                         subtype='mail.mt_comment',
    #                         notification_ids=notification_ids,
    #                         partner_ids=[emp_user_id.id],
    #                     )
    #             is_restrict = self.check_remaining_budget()

                # if not is_restrict.get("is_restrict"):
                # # if self.total_amount <= self.remaining_budget:
                #     res = super(HrExpenseSheetExtend,
                #                 self).action_sheet_move_post()
                #     self.account_move_ids.write({'expense_sheet_id': self.id})
                #     # for move in self.account_move_ids:
                #     #     move.expense_sheet_id = self.id
                #
                #     emp_advance = self.env.ref(
                #         "hr_expense_advance_clearing.product_emp_advance")
                    # for sheet in self:
                    #     move_lines = sheet.account_move_ids.mapped(
                    #         "line_ids") + sheet.advance_sheet_id.account_move_ids.mapped(
                    #         "line_ids")
                    #     account_id = emp_advance.property_account_expense_id.id
                    #
                    #     adv_move_lines = self.env[
                    #         "account.move.line"].sudo().search([
                    #         ("id", "in", move_lines.ids),
                    #         ("account_id", "=", account_id)
                    #     ])
        #
        #             return res
        #         else:
        #             raise UserError(
        #                 _("You don't have enough amount in your budget.Please check %s",is_restrict.get('an_account').name))
        #
        # else:
        #     res = super(HrExpenseSheetExtend, self).action_sheet_move_post()
            # self.account_move_ids.write({'expense_sheet_id': self.id})
            # # for move in self.account_move_ids:
            # #     move.expense_sheet_id = self.id
            #
            # emp_advance = self.env.ref(
            #     "hr_expense_advance_clearing.product_emp_advance")
            # for sheet in self:
            #     move_lines = sheet.account_move_ids.mapped(
            #         "line_ids") + sheet.advance_sheet_id.account_move_ids.mapped(
            #         "line_ids")
            #     account_id = emp_advance.property_account_expense_id.id
            #
            #     adv_move_lines = self.env["account.move.line"].sudo().search([
            #         ("id", "in", move_lines.ids),
            #         ("account_id", "=", account_id)
            #     ])

            # return res


    # def open_clear_advance(self):
    #     self.ensure_one()
    #     action = self.env.ref(
    #         "hr_expense_advance_clearing." "action_hr_expense_sheet_advance_clearing"
    #     )
    #     vals = action.read()[0]
    #     context1 = vals.get("context", {})
    #
    #     if context1:
    #         context1 = safe_eval(context1)
    #     context1["default_advance_sheet_id"] = self.id
    #     context1["default_user_ids"] = [(6, 0, self.user_ids.ids)]
    #     context1["default_contract_id"] = self.contract_id.id
    #     context1["default_analytic_account_id"] = self.analytic_account_id.id
    #     context1["default_advance_sheet_residual"] = self.clearing_residual
    #     vals["context"] = context1
    #     return vals


    # @api.onchange('advance_sheet_id')
    # def _onchange_advance_sheet_id(self):
    #     self.contract_id = self.advance_sheet_id.contract_id.id
    #     self.analytic_account_id = self.advance_sheet_id.analytic_account_id.id
    #     self.user_ids = self.advance_sheet_id.user_ids.ids
    #     self.advance_sheet_residual = self.advance_sheet_id.clearing_residual
    #     self.clearng_amount = self.advance_sheet_id.clearng_amount


class CustomAccountAnalyticAccount(models.Model):
    _inherit = 'account.analytic.account'

    # remaining_budget_amount = fields.Float(string="Remaining Budget",
    #                                        compute='compute_remaining_budget')

    remaining_budget_amount = fields.Float(string="Remaining Budget")

    # TODO: The below content is commented because it is not required in the latest database.The related functionality is no longer part of the current business process.Kept only for reference during migration and validation.


    # @api.depends('line_ids','budget_line_ids')
    # def compute_remaining_budget(self):
    #     """
    #     This method calculates the remaining budget amount from cost and revenue
    #     of an analytic account.
    #     """
    #     for rec in self:
    #         tot_amount = 0
    #         total_exp = 0
    #         total = 0
    #         budgets = rec.budget_line_ids if rec.budget_line_ids else self.env['budget.line'].search([("auto_account_id","in",[rec.id])])
    #         tot_amount = sum(budgets.mapped("budget_amount"))
    #         # tot_amount = sum(self.env['budget.line'].search([('auto_account_id','=',rec.id)]).budget_line_ids.mapped("budget_amount"))
    #         line_ids = rec.line_ids if rec.line_ids else self.env['account.analytic.line'].search([("auto_account_id", "in", [rec.id] )])
    #         for line in line_ids:
    #             total = total + round(line.amount, 2)
    #             product_id = self.env.ref('hr_expense_advance_clearing.product_emp_advance')
    #             if line.product_id.id == product_id.id:
    #                 amt = abs(round(line.amount, 2))
    #                 if line.x_studio_residual < amt or line.x_studio_residual == 0:
    #                     total_exp = total_exp + line.amount
    #
    #         rem = abs(round(total, 2)) - abs(round(total_exp, 2))
    #         rec.remaining_budget_amount = round(tot_amount, 2) - round(rem, 2)
    #

class CustomAccountAnalyticline(models.Model):
    _inherit = 'account.analytic.line'

    # x_studio_residual = fields.Monetary(string="Residual",
    #                                     compute='compute_residual_amount'
    #                                     )

    x_studio_residual = fields.Monetary(string="Residual")

    # TODO: The below content is commented because it is not required in the latest database.The related functionality is no longer part of the current business process.Kept only for reference during migration and validation.


    # def compute_residual_amount(self):
    #     """
    #     Compute residual amount of an expense report.
    #     """
    #     for rec in self:
    #         rec.x_studio_residual = rec.move_line_id.expense_id.sheet_id.clearing_residual


class HrExpenseExtend(models.Model):
    _inherit = 'hr.expense'

    # remaining_budget = fields.Float(string="Remaining budget", readonly=True,
    #                                 related='analytic_account_id.remaining_budget_amount')

    # price_unit = fields.Float(
    #     string="Unit Price",
    #     compute='_compute_price_unit', precompute=True,
    #     required=True, readonly=False,
    #     copy=True,
    #     digits='Product Price',
    # )
    #
    # total_amount = fields.Monetary(
    #     string="Total",
    #     currency_field='company_currency_id',
    #     compute='_compute_total_amount', inverse='_inverse_total_amount',
    #     precompute=True, store=True, readonly=True,
    #     tracking=True,
    # )

    
    # @api.onchange('price_unit', 'quantity')
    # def _inverse_price_unit(self):
    #     print("inverse")
    #     """
    #     Updates total_amount when price_unit is manually changed.
    #     """
    #     for expense in self:
    #         print("expense")
    #         if expense.state not in {'draft', 'reported'}:
    #             continue
    #         # Recalculate total_amount based on new price_unit
    #         expense.total_amount = expense.price_unit * expense.quantity



    # @api.depends('date', 'total_amount', 'currency_id',
    #              'company_currency_id')
    # def _compute_total_amount_currency(self):
    #     for expense in self:
    #         amount = 0
    #         if expense.currency_id and expense.company_currency_id:
    #             date_expense = expense.date or fields.Date.today()
    #             print("total_amount", expense.total_amount)
    #             amount = expense.currency_id._convert(
    #                 expense.total_amount,
    #                 expense.company_currency_id,
    #                 expense.company_id,
    #                 date_expense
    #             )
    #             print("if amount", amount)
    #         print("amount yyyyyyyyyyyyyyy", amount)
    #         expense.total_amount_currency = amount

    # @api.depends('total_amount', 'total_amount_currency')
    # def _compute_price_unit(self):
    #     """
    #        The price_unit is the unit price of the product if no product is set and no attachment overrides it.
    #        Otherwise it is always computed from the total_amount and the quantity else it would break the vendor bill
    #        when edited after creation.
    #     """
    #     for expense in self:
    #         if expense.state not in {'draft', 'reported'}:
    #             continue
    #         product_id = expense.product_id
    #         if expense._needs_product_price_computation():
    #             expense.price_unit = product_id._price_compute(
    #                 'standard_price',
    #                 uom=expense.product_uom_id,
    #                 company=expense.company_id,
    #             )[product_id.id]
    #         else:
    #             print("sss")
                # expense.price_unit = expense.company_currency_id.round(expense.total_amount / expense.quantity) if expense.quantity else 0.

        # @api.depends(
        #     'date',
        #     'company_id',
        #     'currency_id',
        #     'company_currency_id',
        #     'is_multiple_currency',
        #     'total_amount_currency',
        #     'product_id',
        #     'employee_id.user_id.partner_id',
        #     'quantity',
        # )
        # def _compute_total_amount(self):
        #     print("_compute_total_amount")
        #     AccountTax = self.env['account.tax']
        #     for expense in self:
        #         print("_compute_total_amount_currency", expense)
        #         if expense.is_multiple_currency:
        #             taxes = expense.tax_ids.compute_all(expense.price_unit,
        #                                                 expense.currency_id,
        #                                                 expense.quantity,
        #                                                 expense.product_id,
        #                                                 expense.employee_id.user_id.partner_id)
        #             expense.total_amount = taxes.get('total_included')
        #             print("exxxxxxx", expense.total_amount)
        #         else:  # Mono-currency case computation shortcut
        #             expense.total_amount = expense.total_amount_currency
        #             print("dfrthnj", expense.total_amount)

    # @api.depends(
    #     'date',
    #     'company_id',
    #     'currency_id',
    #     'company_currency_id',
    #     'is_multiple_currency',
    #     'total_amount_currency',
    #     'product_id',
    #     'employee_id.user_id.partner_id',
    #     'quantity',
    # )
    # def _compute_total_amount(self):
    #     print("_compute_total_amount")
    #     AccountTax = self.env['account.tax']
    #     for expense in self:
    #         if expense.is_multiple_currency:
    #             base_line = expense._prepare_base_line_for_taxes_computation(
    #                 price_unit=expense.total_amount_currency * expense.currency_rate,
    #                 quantity=1.0,
    #                 currency_id=expense.company_currency_id,
    #                 rate=1.0,
    #             )
    #             AccountTax._add_tax_details_in_base_line(base_line,
    #                                                      expense.company_id)
    #             AccountTax._round_base_lines_tax_details([base_line],
    #                                                      expense.company_id)
    #             expense.total_amount = expense.price_unit * expense.quantity
    #         # else:  # Mono-currency case computation shortcut
    #         #     expense.total_amount = expense.total_amount_currency
    #         #     print("dfrthnj")
    #
    #
    # def action_move_create(self):
    #     '''
    #     main function that is called when trying to create the accounting entries related to an expense
    #     '''
    #     move_group_by_sheet = self._get_account_move_by_sheet()
    #
    #     move_line_values_by_expense = self._get_account_move_line_values()
    #
    #     move_to_keep_draft = self.env['account.move']
    #
    #     company_payments = self.env['account.payment']
    #
    #     for expense in self:
    #         company_currency = expense.company_id.currency_id
    #         different_currency = expense.currency_id != company_currency
    #
    #         # get the account move of the related sheet
    #         move = move_group_by_sheet[expense.sheet_id.id]
    #
    #         # get move line values
    #         move_line_values = move_line_values_by_expense.get(expense.id)
    #         move_line_dst = move_line_values[-1]
    #         total_amount = move_line_dst['debit'] or -move_line_dst['credit']
    #         total_amount_currency = move_line_dst['amount_currency']
    #
    #         # create one more move line, a counterline for the total on payable account
    #         if expense.payment_mode == 'company_account':
    #             if not expense.sheet_id.payment_method_line_id.default_credit_account_id:
    #                 raise UserError(
    #                     _("No credit account found for the %s journal, please configure one.") % (
    #                         expense.sheet_id.payment_method_line_id.name))
    #             journal = expense.sheet_id.payment_method_line_id
    #             # create payment
    #             payment_methods = journal.outbound_payment_method_ids if total_amount < 0 else journal.inbound_payment_method_ids
    #             journal_currency = journal.currency_id or journal.company_id.currency_id
    #             payment = self.env['account.payment'].create({
    #                 'payment_method_id': payment_methods and payment_methods[
    #                     0].id or False,
    #                 'payment_type': 'outbound' if total_amount < 0 else 'inbound',
    #                 'partner_id': expense.employee_id.address_home_id.commercial_partner_id.id,
    #                 'partner_type': 'supplier',
    #                 'journal_id': journal.id,
    #                 'payment_date': expense.date,
    #                 'state': 'draft',
    #                 'currency_id': expense.currency_id.id if different_currency else journal_currency.id,
    #                 'amount': abs(
    #                     total_amount_currency) if different_currency else abs(
    #                     total_amount),
    #                 'name': expense.name,
    #             })
    #
    #             move_line_dst['payment_id'] = payment.id
    #
    #         # link move lines to move, and move to expense sheet
    #         move.write(
    #             {'line_ids': [(0, 0, line) for line in move_line_values]})
    #         expense.sheet_id.write({'account_move_ids': move.id})
    #
    #         for line in move.line_ids:
    #             if not line.currency_id:
    #                 if line.debit:
    #                     line.amount_currency = line.debit
    #                 else:
    #                     line.amount_currency = -(line.credit)
    #
    #             if line.debit == 0.0 and line.credit == 0.0:
    #                 line.unlink()
    #         if expense.payment_mode == 'company_account':
    #             company_payments |= payment
    #             if journal.post_at == 'bank_rec':
    #                 move_to_keep_draft |= move
    #
    #             expense.sheet_id.paid_expense_sheets()
    #
    #     company_payments.filtered(
    #         lambda x: x.journal_id.post_at == 'pay_val').write(
    #         {'state': 'reconciled'})
    #     company_payments.filtered(
    #         lambda x: x.journal_id.post_at == 'bank_rec').write(
    #         {'state': 'posted'})
    #
    #     # post the moves
    #     for move in move_group_by_sheet.values():
    #         if move in move_to_keep_draft:
    #             continue
    #         move.post()
    #
    #     return move_group_by_sheet
    #

class HrExpense(models.Model):
    _inherit = 'hr.expense'

    budget_reponsibles = fields.Many2many(related='sheet_id.budget_reponsibles',
                                          readonly=True)
