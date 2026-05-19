# Copyright 2019 Kitti Upariphutthiphong <kittiu@ecosoft.co.th>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import ast

from odoo import Command, api, fields, models, _
from odoo.exceptions import ValidationError, UserError
from odoo.tools import float_compare, float_is_zero


class HrExpenseSheet(models.Model):
    _inherit = "hr.expense.sheet"

    advance = fields.Boolean(
        string="Employee Advance",
    )
    journal_id = fields.Many2one(
        comodel_name="account.journal",
        string="Expense Journal",
        compute="_compute_journal_id",
        store=True,
        readonly=False,
        inverse="_inverse_journal_id",
        check_company=True,
    )

    def _inverse_journal_id(self):
        for sheet in self:
            if sheet.payment_mode == "own_account":
                sheet.employee_journal_id = sheet.journal_id
    advance_sheet_id = fields.Many2one(
        comodel_name="hr.expense.sheet",
        string="Clear Advance",
        domain="[('advance', '=', True), ('employee_id', '=', employee_id),"
               " ('clearing_residual', '>', 0.0)]",
        help="Show remaining advance of this employee",
    )
    clearing_sheet_ids = fields.One2many(
        comodel_name="hr.expense.sheet",
        inverse_name="advance_sheet_id",
        string="Clearing Sheet",
        readonly=True,
        help="Show reference clearing on advance",
    )
    clearing_count = fields.Integer(
        compute="_compute_clearing_count",
    )
    payment_return_ids = fields.One2many(
        comodel_name="account.payment",
        inverse_name="advance_id",
        string="Payment Return",
        readonly=True,
        help="Show reference return advance on advance",
    )
    return_count = fields.Integer(compute="_compute_return_count")
    clearing_residual = fields.Monetary(
        string="Amount to clear",
        compute="_compute_clearing_residual",
        store=True,
        help="Amount to clear of this expense sheet in company currency",
    )
    advance_sheet_residual = fields.Monetary(
        string="Advance Remaining",
        related="advance_sheet_id.clearing_residual",
        store=True,
        help="Remaining amount to clear the selected advance sheet",
    )
    amount_payable = fields.Monetary(
        string="Payable Amount",
        compute="_compute_amount_payable",
        help="Final regiter payment amount even after advance clearing",
    )
    is_old_data = fields.Boolean(
        compute="_compute_old_data",
        string="Old Data", help="Field to check if this is old data(to set old record readonly)"
    )

    def _compute_old_data(self):
        """Field to check if this is old data(to set old record readonly)"""
        restored_date = self.env['ir.config_parameter'].sudo().get_param(
            'hr_expense_advance_clear.restored_date')
        force_edit_old_data = self.env['ir.config_parameter'].sudo().get_param(
            'hr_expense_advance_clear.force_edit_old_data')
        restored_date = (
            fields.Datetime.from_string(restored_date)
            if restored_date else False
        )
        for record in self:
            if force_edit_old_data or not restored_date or not record.create_date:
                # If force_edit is enabled or no restored_date, allow editing
                record.is_old_data = False
            else:
                # else check if the record is created before the restored date and restrict editing if it becomes true
                record.is_old_data = record.create_date.date() < restored_date.date()

    @api.constrains("advance_sheet_id", "expense_line_ids")
    def _check_advance_expense(self):
        advance_lines = self.expense_line_ids.filtered("advance")
        if self.advance_sheet_id and advance_lines:
            raise ValidationError(
                self.env._("Advance clearing must not contain any advance expense line")
            )
        if advance_lines and len(advance_lines) != len(self.expense_line_ids):
            raise ValidationError(
                self.env._("Advance must contain only advance expense line")
            )

    @api.depends("account_move_ids.payment_state", "account_move_ids.amount_residual")
    def _compute_from_account_move_ids(self):
        """After clear advance.
        if amount residual is zero, payment state will change to 'paid'
        """
        res = super()._compute_from_account_move_ids()
        for sheet in self:
            if sheet.advance_sheet_id and any(m.state == "posted" for m in sheet.account_move_ids):
                emp_advance = sheet._get_product_advance()
                adv_account = emp_advance.with_company(sheet.company_id).property_account_expense_id if emp_advance else False

                # Identify if this move HAS standard payable/receivable components (the reimbursable part)
                valid_types = self.env['account.payment']._get_valid_payment_account_types()
                has_reimbursable = any(l.account_id.account_type in valid_types for l in sheet.account_move_ids.line_ids)

                # If it's a reimbursable expense (Expense > Advance), we only care about the standard payable lines.
                # If it's clearing-only (Expense < Advance), we still sum the advance clearing part so it stays "Not Paid".
                rec_lines = sheet.account_move_ids.line_ids.filtered(
                    lambda x: x.credit and x.account_id.reconcile and not x.reconciled
                )
                if has_reimbursable:
                    rec_lines = rec_lines.filtered(lambda x: x.account_id != adv_account)

                actual_payable = -sum(rec_lines.mapped("amount_residual"))

                if float_is_zero(actual_payable, precision_rounding=sheet.currency_id.rounding):
                    sheet.payment_state = "paid"
                    sheet.amount_residual = 0.0
                else:
                    sheet.payment_state = "not_paid"
                    sheet.amount_residual = actual_payable
        return res

    @api.depends('advance_sheet_id.clearing_residual', 'payment_state', 'approval_state')
    def _compute_state(self):
        super()._compute_state()
        for sheet in self:
            if sheet.advance_sheet_id and sheet.account_move_ids:
                if any(m.state == "posted" for m in sheet.account_move_ids):
                    if sheet.payment_state not in ("paid", "in_payment", "reversed"):
                        if not float_is_zero(
                            sheet.advance_sheet_id.clearing_residual,
                            precision_rounding=sheet.currency_id.rounding,
                        ):
                            sheet.state = "post"
                        else:
                            sheet.state = "done"

    def _get_product_advance(self):
        return self.env.ref("hr_expense_advance_clear.product_emp_advance", False)

    @api.depends("account_move_ids.line_ids.amount_residual")
    def _compute_clearing_residual(self):
        for sheet in self:
            emp_advance = sheet._get_product_advance()
            residual_company = 0.0
            if emp_advance:
                property_account_expense_id = emp_advance.with_company(
                    sheet.company_id
                ).property_account_expense_id
                for line in sheet.sudo().account_move_ids.line_ids:
                    if line.account_id == property_account_expense_id:
                        residual_company += line.amount_residual
            sheet.clearing_residual = residual_company

    def _compute_amount_payable(self):
        for sheet in self:
            rec_lines = sheet.account_move_ids.line_ids.filtered(
                lambda x: x.credit and x.account_id.reconcile and not x.reconciled
            )
            sheet.amount_payable = -sum(rec_lines.mapped("amount_residual"))

    @api.depends("clearing_sheet_ids")
    def _compute_clearing_count(self):
        for sheet in self:
            sheet.clearing_count = len(sheet.clearing_sheet_ids)

    @api.depends("payment_return_ids")
    def _compute_return_count(self):
        for sheet in self:
            sheet.return_count = len(sheet.payment_return_ids)

    def action_sheet_move_post(self):
        """Post journal entries with clearing document"""
        res = super().action_sheet_move_post()
        for sheet in self:
            if sheet.is_old_data:
                # raise error while using this method in old datas
                raise UserError(
                    _("sorry, You cannot update this data. This is old data."))
            if not sheet.advance_sheet_id:
                continue

            total_expenses_amount = sum(
                sheet.advance_sheet_id.clearing_sheet_ids.filtered(
                    lambda s: s.state in ('post', 'done') or s.id in self.ids
                ).mapped('total_amount')
            )

            # ONLY reconcile automatically if sum >= advance amount.
            if float_compare(total_expenses_amount, sheet.advance_sheet_id.total_amount, precision_rounding=sheet.currency_id.rounding) >= 0:
                sheet._reconcile_advance_clearing()

        return res

    def _reconcile_advance_clearing(self):
        for sheet in self:
            if not sheet.advance_sheet_id:
                continue
            move_lines = sheet.advance_sheet_id.account_move_ids.line_ids
            # Include all clearing sheets to ensure we reconcile whatever is available
            for clearing_sheet in sheet.advance_sheet_id.clearing_sheet_ids.filtered(lambda s: s.state != 'cancel'):
                move_lines |= clearing_sheet.account_move_ids.line_ids

            emp_advance = sheet._get_product_advance()
            account_id = emp_advance.property_account_expense_id.id
            adv_move_lines = (
                self.env["account.move.line"]
                .sudo()
                .search(
                    [
                        ("id", "in", move_lines.ids),
                        ("account_id", "=", account_id),
                        ("reconciled", "=", False),
                    ]
                )
            )
            if adv_move_lines:
                adv_move_lines.reconcile()

        return True

    def _get_move_line_vals(self):
        self.ensure_one()
        move_line_vals = []
        advance_to_clear = self.advance_sheet_residual
        emp_advance = self._get_product_advance()
        account_advance = emp_advance.property_account_expense_id

        # The advance expense lines always carry the original total_amount_currency
        # in the correct foreign currency (IQD), so we use that as the exact source.
        advance_to_clear_currency_exact = sum(
            self.advance_sheet_id.expense_line_ids.mapped("total_amount_currency")
        )

        for expense in self.expense_line_ids:
            move_line_name = (
                f"{expense.employee_id.name}: {expense.name.splitlines()[0][:64]}"
            )
            partner_id = expense.employee_id.sudo().work_contact_id.id

            total_amount = -expense.total_amount
            total_amount_currency = -expense.total_amount_currency

            # Source move line
            move_line_src = expense._get_move_line_src(move_line_name, partner_id)
            move_line_values = [move_line_src]

            # Destination move line
            move_line_dst = expense._get_move_line_dst(
                move_line_name,
                partner_id,
                total_amount,
                total_amount_currency,
                account_advance,
            )

            # Check clearing > advance, it will split line
            credit = move_line_dst["credit"]
            # cr payable -> cr advance
            remain_payable = 0.0
            remain_payable_currency = 0.0
            payable_move_line = []
            rounding = expense.currency_id.rounding
            expense_currency = expense.currency_id

            if (
                float_compare(
                    credit,
                    advance_to_clear,
                    precision_rounding=rounding,
                )
                == 1
            ):
                remain_payable = credit - advance_to_clear
                # Use exact foreign currency from advance move line — not a conversion.
                # This guarantees amount_currency on the clearing line matches the advance line.
                remain_payable_currency = abs(total_amount_currency) - abs(advance_to_clear_currency_exact)
                move_line_dst.update(
                    {
                        "credit": advance_to_clear,
                        "amount_currency": -abs(advance_to_clear_currency_exact),
                        "currency_id": expense_currency.id,
                    }
                )
                advance_to_clear = 0.0
                advance_to_clear_currency_exact = 0.0
                # extra payable line
                account_dest = expense.sheet_id._get_expense_account_destination()
                payable_move_line = move_line_dst.copy()
                payable_move_line.update(
                    {
                        "credit": remain_payable,
                        "amount_currency": -remain_payable_currency,
                        "currency_id": expense_currency.id,
                        "account_id": account_dest,
                    }
                )
            else:
                advance_to_clear -= credit
                advance_to_clear_currency_exact -= abs(total_amount_currency)

            # Add destination first (if credit is not zero)
            if not float_is_zero(move_line_dst["credit"], precision_rounding=rounding):
                move_line_values.append(move_line_dst)
            if payable_move_line:
                move_line_values.append(payable_move_line)
            move_line_vals.extend(move_line_values)
        return move_line_vals

    def _prepare_bills_vals(self):
        """create journal entry instead of bills when clearing document"""
        self.ensure_one()
        res = super()._prepare_bills_vals()
        if self.advance_sheet_id and self.payment_mode == "own_account":
            # Advance Sheets with no residual left
            if self.advance_sheet_residual <= 0.0:
                raise ValidationError(
                    self.env._(
                        "Advance: %(name)s has no amount to clear", name=self.name
                    )
                )
            res.update(
                {
                    "move_type": "entry",
                    "line_ids": [
                        Command.create(vals) for vals in self._get_move_line_vals()
                    ],
                }
            )
        return res

    def _check_can_approve(self):
        """Check advance residual before approval"""
        for sheet in self.filtered("advance_sheet_id"):
            if sheet.advance_sheet_residual <= 0.0:
                raise ValidationError(
                    self.env._(
                        "Advance: %(name)s has no amount to clear",
                        name=sheet.advance_sheet_id.name,
                    )
                )
        return super()._check_can_approve()

    def open_clear_advance(self):
        self.ensure_one()
        result = self.env["ir.actions.act_window"]._for_xml_id(
            "hr_expense_advance_clear.action_hr_expense_sheet_advance_clearing"
        )
        # Add default context
        context = ast.literal_eval(result["context"])
        context.update(
            {
                "default_advance_sheet_id": self.id,
                "default_employee_id": self.employee_id.id,
                "default_budget_policy_id":self.budget_policy_id.id,
                "default_available_amount":self.available_amount,
                "default_user_ids":self.user_ids.ids,
                "default_contract_id":self.contract_id.id,
            }
        )
        result["context"] = context
        return result

    def get_domain_advance_sheet_expense_line(self):
        return self.advance_sheet_id.expense_line_ids.filtered("clearing_product_id")

    def create_clearing_expense_line(self, line):
        clear_advance = self._prepare_clear_advance(line)
        clearing_line = self.env["hr.expense"].new(clear_advance)
        return clearing_line

    @api.onchange("advance_sheet_id")
    def _onchange_advance_sheet_id(self):
        self.expense_line_ids = self.expense_line_ids.filtered(
            lambda line: not line.av_line_id
        )
        if not self.advance_sheet_id:
            return

        self.advance_sheet_id.expense_line_ids.sudo().read(["id"])
        lines = self.get_domain_advance_sheet_expense_line()
        for line in lines:
            self.expense_line_ids += self.create_clearing_expense_line(line)

    def _prepare_clear_advance(self, line):
        # Prepare the clearing expense
        clear_line_dict = {
            "advance": False,
            "name": line.clearing_product_id.display_name,
            "product_id": line.clearing_product_id.id,
            "clearing_product_id": False,
            "date": fields.Date.context_today(self),
            "account_id": False,
            "state": "draft",
            "product_uom_id": False,
            "av_line_id": line.id,
        }
        clear_line = self.env["hr.expense"].new(clear_line_dict)
        clear_line._compute_account_id()  # Set some vals
        # Prepare the original advance line
        adv_dict = line._convert_to_write(line._cache)

        # Remove non-updatable fields
        del_cols = set.union(
            {
                k for k, v in line._fields.items() if v.type == "one2many"
            },  # Remove O2M fields
            self.env["mail.thread"]._fields.keys(),  # Remove mail.thread fields
            self.env["mail.activity.mixin"]._fields.keys(),  # Remove activity fields
            clear_line_dict.keys(),  # Remove already assigned fields
        )
        adv_dict = {k: v for k, v in adv_dict.items() if k not in del_cols}
        # Assign the known value from original advance line
        clear_line.update(adv_dict)
        clearing_dict = clear_line._convert_to_write(clear_line._cache)
        # Convert list of int to [(6, 0, list)]
        clearing_dict = {
            k: isinstance(v, list)
            and all(isinstance(x, int) for x in v)
            and [(6, 0, v)]
            or v
            for k, v in clearing_dict.items()
        }
        return clearing_dict

    def action_open_clearings(self):
        self.ensure_one()
        return {
            "name": self.env._("Clearing Sheets"),
            "type": "ir.actions.act_window",
            "res_model": "hr.expense.sheet",
            "view_mode": "list,form",
            "domain": [("id", "in", self.clearing_sheet_ids.ids)],
        }

    def action_open_payment_return(self):
        self.ensure_one()
        return {
            "name": self.env._("Payment Return"),
            "type": "ir.actions.act_window",
            "res_model": "account.payment",
            "view_mode": "list,form",
            "domain": [("id", "in", self.payment_return_ids.ids)],
        }

    def action_refuse_expense_sheets(self):
        for rec in self:
            if rec.is_old_data:
                # raise error while using this method in old datas
                raise UserError(
                    _("sorry, You cannot update this data. This is old data."))
        return super().action_refuse_expense_sheets()

    def action_reset_expense_sheets(self):
        for sheet in self:
            if sheet.is_old_data:
                raise UserError(
                    _("Sorry, you cannot update this data. This is old data.")
                )
            # Reset all approval lines
            sheet.approval_lines.write({
                'approved': False,
                'approved_date': False,
                'approved_by': False,
            })

            # Remove approval activities
            sheet.activity_unlink(['hr_expense.mail_act_expense_approval'])
        return super(HrExpenseSheet, self).action_reset_expense_sheets()

    def action_register_payment(self):
        for rec in self:
            if rec.is_old_data:
                # raise error while using this method in old datas
                raise UserError(
                    _("sorry, You cannot update this data. This is old data."))

        # If it's a clearing expense, try to reconcile with the advance first.
        # This addresses the case where Expense < Advance and the user wants to "pay" (clear) it manually.
        clearing_sheets = self.filtered(lambda s: s.advance_sheet_id and s.state in ('post', 'done') and s.payment_state != 'paid')
        if clearing_sheets:
            clearing_sheets._reconcile_advance_clearing()

        # If any sheet still has an amount to pay (because Expense > Advance or it's not a clearing), open the wizard.
        sheets_to_pay = self.filtered(lambda s: s.payment_state != 'paid')
        if not sheets_to_pay:
            return True

        action = super(HrExpenseSheet, sheets_to_pay).action_register_payment()
        if any(sheet.advance_sheet_id for sheet in sheets_to_pay):
            action["context"].update({"expense_clearing": True})

        if self.env.context.get("hr_return_advance"):
            action["context"].update(
                {
                    "clearing_sheet_ids": self.clearing_sheet_ids.ids,
                }
            )
        return action
