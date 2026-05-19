from odoo import models, fields, tools, api


class AccountPaymentReport(models.Model):
    _name = 'account.payment.report'
    _description = 'Comprehensive Payment Report'
    _auto = False
    _order = 'payment_date desc'

    id = fields.Id()
    payment_date = fields.Date(string="Date", readonly=True)
    payment_journal_id = fields.Many2one('account.journal', string="Journal", readonly=True)
    payment_move_name = fields.Char(string="Reference", readonly=True)
    partner_id = fields.Many2one('res.partner', string="Partner", readonly=True)
    account_id = fields.Many2one('account.account', string="Account", readonly=True)
    label = fields.Char(string="Label", readonly=True)

    money_in = fields.Monetary(string="Money In", currency_field='currency_id', readonly=True)
    money_out = fields.Monetary(string="Money Out", currency_field='currency_id', readonly=True)
    balance = fields.Monetary(string="Balance", currency_field='currency_id', readonly=True)

    currency_id = fields.Many2one('res.currency', string="Currency", readonly=True)
    company_id = fields.Many2one('res.company', string="Company", readonly=True)

    # payment_move_id is stored in the SQL view to drive the compute
    payment_move_id = fields.Many2one('account.move', string="Payment Move", readonly=True)

    expense_sheet_id = fields.Many2many(
        'hr.expense.sheet',
        string="Expense Report",
        compute='_compute_expense_sheets',
        search='_search_expense_sheet_id',
    )
    invoice_id = fields.Many2many(
        'account.move',
        string="Invoice/Bill",
        compute='_compute_invoices',
        search='_search_invoice_id',
    )
    reconciliation_date = fields.Date(string="Reconciliation Date", readonly=True)

    state = fields.Selection([
        ('draft', "Draft"),
        ('in_process', "In Process"),
        ('paid', "Paid"),
        ('canceled', "Canceled"),
        ('rejected', "Rejected"),
    ], string="Status", readonly=True)

    def _build_reconciliation_maps(self):
        """Single DB query that returns two maps keyed by payment move id:
        - expense_map:  payment_move_id -> hr.expense.sheet recordset
        - invoice_map:  payment_move_id -> account.move recordset
        """
        from collections import defaultdict

        move_ids = self.mapped('payment_move_id').ids
        move_ids_set = set(move_ids)

        expense_map = defaultdict(lambda: self.env['hr.expense.sheet'])
        invoice_map = defaultdict(lambda: self.env['account.move'])

        if not move_ids_set:
            return expense_map, invoice_map

        # One query covers both computes
        reconciles = self.env['account.partial.reconcile'].search([
            '|',
            ('debit_move_id.move_id', 'in', move_ids),
            ('credit_move_id.move_id', 'in', move_ids),
        ])

        # Collect all related move IDs so we can batch-browse them
        related_move_ids = set()
        pair_map = defaultdict(set)  # payment_move_id -> {related_move_id, ...}

        for r in reconciles:
            d_id = r.debit_move_id.move_id.id
            c_id = r.credit_move_id.move_id.id
            if d_id in move_ids_set:
                pair_map[d_id].add(c_id)
                related_move_ids.add(c_id)
            if c_id in move_ids_set:
                pair_map[c_id].add(d_id)
                related_move_ids.add(d_id)

        # Batch-browse all related moves once to get expense_sheet_id
        related_moves = self.env['account.move'].browse(list(related_move_ids))
        move_by_id = {m.id: m for m in related_moves}

        # Also pre-fetch direct expense sheets for payment moves
        payment_moves = self.env['account.move'].browse(move_ids)
        direct_expense = {m.id: m.expense_sheet_id for m in payment_moves}

        for pm_id, related_ids in pair_map.items():
            for rel_id in related_ids:
                if rel_id == pm_id:
                    continue
                rel_move = move_by_id.get(rel_id)
                if not rel_move:
                    continue
                invoice_map[pm_id] |= rel_move
                if rel_move.expense_sheet_id:
                    expense_map[pm_id] |= rel_move.expense_sheet_id

            # Include directly linked expense sheet
            if direct_expense.get(pm_id):
                expense_map[pm_id] |= direct_expense[pm_id]

        return expense_map, invoice_map

    @api.depends('payment_move_id')
    def _compute_expense_sheets(self):
        expense_map, _ = self._build_reconciliation_maps()
        empty = self.env['hr.expense.sheet']
        for rec in self:
            rec.expense_sheet_id = expense_map.get(rec.payment_move_id.id, empty)

    @api.depends('payment_move_id')
    def _compute_invoices(self):
        _, invoice_map = self._build_reconciliation_maps()
        empty = self.env['account.move']
        for rec in self:
            rec.invoice_id = invoice_map.get(rec.payment_move_id.id, empty)

    def _search_expense_sheet_id(self, operator, value):
        if operator in ('ilike', 'like', '=', 'in'):
            if isinstance(value, str):
                sheets = self.env['hr.expense.sheet'].search([('name', operator, value)])
            else:
                sheets = self.env['hr.expense.sheet'].search([('id', operator, value)])
            sheet_ids = tuple(sheets.ids)

            if not sheet_ids:
                return [('id', '=', -1)]

            query = """
                SELECT pay_aml.move_id
                FROM account_partial_reconcile apr
                JOIN account_move_line pay_aml ON pay_aml.id IN (apr.debit_move_id, apr.credit_move_id)
                JOIN account_move_line inv_aml ON inv_aml.id IN (apr.debit_move_id, apr.credit_move_id) AND inv_aml.id != pay_aml.id
                JOIN account_move inv ON inv.id = inv_aml.move_id
                WHERE inv.expense_sheet_id IN %s
                UNION
                SELECT am.id
                FROM account_move am
                WHERE am.expense_sheet_id IN %s
            """
            self.env.cr.execute(query, (sheet_ids, sheet_ids))
            move_ids = [r[0] for r in self.env.cr.fetchall()]
            if not move_ids:
                return [('id', '=', -1)]
            return [('payment_move_id', 'in', move_ids)]
        return []

    def _search_invoice_id(self, operator, value):
        if operator in ('ilike', 'like', '=', 'in'):
            if isinstance(value, str):
                invoices = self.env['account.move'].search([
                    ('name', operator, value),
                    ('move_type', 'in', ('out_invoice', 'out_refund', 'in_invoice', 'in_refund'))
                ])
            else:
                invoices = self.env['account.move'].search([
                    ('id', operator, value),
                    ('move_type', 'in', ('out_invoice', 'out_refund', 'in_invoice', 'in_refund'))
                ])
            invoice_ids = tuple(invoices.ids)

            if not invoice_ids:
                return [('id', '=', -1)]

            query = """
                SELECT pay_aml.move_id
                FROM account_partial_reconcile apr
                JOIN account_move_line pay_aml ON pay_aml.id IN (apr.debit_move_id, apr.credit_move_id)
                JOIN account_move_line inv_aml ON inv_aml.id IN (apr.debit_move_id, apr.credit_move_id) AND inv_aml.id != pay_aml.id
                WHERE inv_aml.move_id IN %s
            """
            self.env.cr.execute(query, (invoice_ids,))
            move_ids = [r[0] for r in self.env.cr.fetchall()]
            if not move_ids:
                return [('id', '=', -1)]
            return [('payment_move_id', 'in', move_ids)]
        return []

    def init(self):
        tools.drop_view_if_exists(self.env.cr, self._table)
        self.env.cr.execute("""
            CREATE OR REPLACE VIEW account_payment_report AS (
                WITH reconciliation_info AS (
                    SELECT
                        pay_aml_rec.move_id AS payment_move_id,
                        MAX(apr.max_date) AS reconciliation_date
                    FROM account_partial_reconcile apr
                    JOIN account_move_line pay_aml_rec
                        ON (pay_aml_rec.id = apr.debit_move_id OR pay_aml_rec.id = apr.credit_move_id)
                    JOIN account_move_line inv_aml_rec
                        ON (inv_aml_rec.id = apr.debit_move_id OR inv_aml_rec.id = apr.credit_move_id)
                        AND inv_aml_rec.id != pay_aml_rec.id
                    JOIN account_move inv_am ON inv_am.id = inv_aml_rec.move_id
                    GROUP BY pay_aml_rec.move_id
                )
                SELECT
                    aml.id                      AS id,
                    aml.date                    AS payment_date,
                    aml.journal_id              AS payment_journal_id,
                    am.id                       AS payment_move_id,
                    am.name                     AS payment_move_name,
                    aml.partner_id              AS partner_id,
                    aml.account_id              AS account_id,
                    aml.debit                   AS money_in,
                    aml.credit                  AS money_out,
                    aml.balance                 AS balance,
                    aml.company_currency_id     AS currency_id,
                    aml.company_id              AS company_id,
                    aml.name                    AS label,
                    COALESCE(ap.state, CASE WHEN ri.reconciliation_date IS NOT NULL THEN 'paid' ELSE 'in_process' END) AS state,
                    ri.reconciliation_date       AS reconciliation_date
                FROM account_move_line aml
                JOIN account_move am ON am.id = aml.move_id
                JOIN account_journal aj ON aj.id = aml.journal_id
                LEFT JOIN (
                    SELECT DISTINCT ON (move_id) move_id, state
                    FROM account_payment
                    ORDER BY move_id, (state != 'draft') DESC, id DESC
                ) ap ON ap.move_id = am.id
                LEFT JOIN reconciliation_info ri ON ri.payment_move_id = am.id
                WHERE aml.parent_state = 'posted'
                  AND aj.type IN ('bank', 'cash')
                  AND aml.account_id = aj.default_account_id
            );
        """)
