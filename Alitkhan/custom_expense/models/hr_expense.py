from odoo import models, fields, api


class HrExpense(models.Model):
    _inherit = "hr.expense"

    # currency_id = fields.Many2one(
    #     comodel_name='res.currency',
    #     string="Currency",
    #     compute='_compute_currency_id', precompute=True, store=True, readonly=False,
    #     required=True,
    #     states={'draft': [('readonly', False)],
    #             'refused': [('readonly', False)]},
    #     default=lambda self: self.env.company.currency_id,
    #     domain=lambda self: self._get_currency_domain()
    # )

    currency_id = fields.Many2one(
        comodel_name='res.currency',
        string="Currency",
        compute='_compute_currency_id', precompute=True, store=True, readonly=False,
        required=True,
        states={'draft': [('readonly', False)],
                'refused': [('readonly', False)]},
        default=lambda self: self.env.company.currency_id,
    )
    custom_payment_mode = fields.Selection(
        selection=[
            ('own_account', 'Paid by Employee'),
            ('company_account', 'Paid by Company'),
        ],
        string="Paid By",
        default='own_account',
        required=True,
        tracking=True,
        help="Select who paid for this expense. "
             "Paid by Employee: the employee paid and will be reimbursed. "
             "Paid by Company: the company paid directly.",
    )
    payment_mode = fields.Selection(
        selection=[
            ('own_account', "Employee (to reimburse)"),
            ('company_account', "Company")
        ],
        string="Odoo's Paid By",
        default='own_account',
        required=True,
        tracking=True,
    )

    def action_update_custom_payment_mode(self):
        """
        Update custom_payment_mode from payment_mode
        for records where custom_payment_mode is empty or NULL
        """
        self.env.cr.execute("""
            UPDATE hr_expense
            SET custom_payment_mode = payment_mode
            WHERE custom_payment_mode IS NULL OR custom_payment_mode = '' or custom_payment_mode = 'own_account'
        """)
        self.env.cr.commit()

        # Return notification to user
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'message': 'Custom Payment Mode updated successfully!',
                'type': 'success',
                'sticky': False,
            }
        }

    @api.depends('product_id', 'company_id')
    def _compute_price_unit(self):
        # Store previous prices to protect them from being zeroed out by Category selection
        old_prices = []
        for e in self:
            price = e.price_unit
            # If we are in an onchange (NewId) and the price is 0, fallback to the original saved record
            if price == 0 and e._origin:
                price = e._origin.price_unit
            old_prices.append(price)
        
        # Let Odoo's native calculation evaluate the price based on the category
        super(HrExpense, self)._compute_price_unit()
        
        for e, old_price in zip(self, old_prices):
            # If changing the Category caused Odoo to forcefully drop the price_unit to 0,
            # but we had previously entered a valid amount, block it by restoring the old amount.
            if e.price_unit == 0 and old_price != 0:
                e.price_unit = old_price

    @api.depends('quantity', 'price_unit', 'tax_ids')
    def _compute_total_amount_currency(self):
        old_totals = []
        for e in self:
            total = e.total_amount_currency
            if total == 0 and e._origin:
                total = e._origin.total_amount_currency
            old_totals.append(total)

        super(HrExpense, self)._compute_total_amount_currency()

        for e, old_total in zip(self, old_totals):
            if e.total_amount_currency == 0 and old_total != 0:
                e.total_amount_currency = old_total

    def onchange(self, values, field_names, fields_spec):
        if self and len(self) == 1 and isinstance(field_names, list):
            ui_curr = values.get('total_amount_currency')
            ui_tot = values.get('total_amount')
            if ui_curr is not None and ui_tot is not None:
                if 'total_amount_currency' not in field_names:
                    # If user reverted to origin, but total_amount is polluted, force a recompute
                    if ui_curr == self.total_amount_currency and ui_tot != self.total_amount:
                        field_names.append('total_amount_currency')
            
            ui_curr_id = values.get('currency_id')
            if ui_curr_id is not None and ui_tot is not None:
                if 'currency_id' not in field_names:
                    if ui_curr_id == self.currency_id.id and ui_tot != self.total_amount:
                        field_names.append('currency_id')

        return super(HrExpense, self).onchange(values, field_names, fields_spec)

    @api.depends('currency_id', 'total_amount_currency', 'date', 'total_amount')
    def _compute_currency_rate(self):
        super(HrExpense, self)._compute_currency_rate()
        for expense in self:
            if expense.is_multiple_currency and expense._origin:
                if (
                        expense.currency_id == expense._origin.currency_id
                        and expense.total_amount_currency == expense._origin.total_amount_currency
                        and expense.date == expense._origin.date
                ):
                    expense.currency_rate = expense._origin.total_amount / expense._origin.total_amount_currency if expense._origin.total_amount_currency else 1.0

    @api.depends(
        'date', 'company_id', 'currency_id', 'company_currency_id',
        'is_multiple_currency', 'total_amount_currency', 'product_id',
        'employee_id.user_id.partner_id', 'quantity'
    )
    def _compute_total_amount(self):
        old_totals = []
        for e in self:
            total = e.total_amount
            if total == 0 and e._origin:
                total = e._origin.total_amount
            old_totals.append(total)

        super(HrExpense, self)._compute_total_amount()

        for e, old_total in zip(self, old_totals):
            if e.total_amount == 0 and old_total != 0:
                e.total_amount = old_total

    def action_get_attachment_view(self):
        self.ensure_one()
        res = super(HrExpense, self).action_get_attachment_view()
        res.pop('id', None)
        res.pop('xml_id', None)
        return res

    # TODO: The below content is commented because it is not required in the latest database.The related functionality is no longer part of the current business process.Kept only for reference during migration and validation.


    #
    # def _get_currency_domain(self):
    #     users = []
    #     users += self.env.ref("account.group_account_user").users.ids
    #     users += self.env.ref("account.group_account_manager").users.ids
    #     users += self.env.ref("account.group_account_invoice").users.ids
    #     # users += self.env.ref("account.cashier").users.ids
    #     currencies = (self.env['ir.config_parameter'].sudo().get_param(
    #      'custom_expense.limited_currency_ids'))
    #     if self.env.user.id in users:
    #         domain = []
    #     else:
    #         currency = currencies.translate(
    #             {ord(c): None for c in "[]"})
    #
    #         li = list(currency.split(","))
    #         domain = [('id', 'in', li)]
    #     return domain
