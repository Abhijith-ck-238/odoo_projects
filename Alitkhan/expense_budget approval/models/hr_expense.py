from odoo import models, fields


class HrExpense(models.Model):
    _inherit = "hr.expense"

    currency_id = fields.Many2one(
        comodel_name='res.currency',
        string="Currency",
        compute='_compute_currency_id', precompute=True, store=True, readonly=False,
        required=True,
        states={'draft': [('readonly', False)],
                'refused': [('readonly', False)]},
        default=lambda self: self.env.company.currency_id,
        domain=lambda self: self._get_currency_domain()
    )


    def _get_currency_domain(self):
        users = []
        users += self.env.ref("account.group_account_user").users.ids
        users += self.env.ref("account.group_account_manager").users.ids
        users += self.env.ref("account.group_account_invoice").users.ids
        # users += self.env.ref("account.cashier").users.ids

        currencies = self.env['ir.config_parameter'].sudo().get_param(
            'custom_expense.limited_currency_ids'
        )
        print("currency", currencies)

        if self.env.user.id in users:
            domain = []
        else:
            currency = currencies.translate(
                {ord(c): None for c in "[]"})

            li = list(currency.split(","))
            domain = [('id', 'in', li)]
        return domain
