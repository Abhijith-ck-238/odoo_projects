from odoo import models, api, fields,Command
from odoo.tools import date_utils


class HrExpenseSheet(models.Model):
    _inherit = "hr.expense.sheet"

    nb_attachment = fields.Integer(string="Number of Attachments",
                                   compute='_compute_nb_attachment')
    custom_payment_mode = fields.Selection(
        related='expense_line_ids.custom_payment_mode',
        string="Paid By",
        tracking=True,
        readonly=True,
    )
    payment_mode = fields.Selection(
        related='expense_line_ids.payment_mode',
        string="Odoo's Paid By",
        tracking=True,
        readonly=True,
    )

    @api.depends('expense_line_ids.attachment_ids')
    def _compute_nb_attachment(self):
        for sheet in self:
            sheet.nb_attachment = self.env['ir.attachment'].search_count([
                ('res_model', '=', 'hr.expense'),
                ('res_id', 'in', sheet.expense_line_ids.ids),
            ])

    # def _calculate_default_accounting_date(self):
    #     """
    #     Override to ensure the accounting date is never set to a prior year.
    #     The standard logic can return a date capped to the end of the expense's
    #     month (e.g. 31/12/2025) when expense dates are older than the current
    #     month. This causes the journal entry sequence to use the wrong year.
    #     """
    #     accounting_date = super()._calculate_default_accounting_date()
    #     today = fields.Date.context_today(self)
    #     year_start = date_utils.start_of(today, 'year')
    #     if accounting_date < year_start:
    #         return today
    #     return accounting_date

    # def _do_create_moves(self):
    #     """
    #     Override to clear any stale accounting_date that belongs to a prior
    #     year before the draft account.move is created.
    #
    #     The standard code (line 767 in hr_expense_sheet.py):
    #         sheet.accounting_date = sheet.accounting_date or ...
    #     will reuse a previously stored accounting_date even if it is from a
    #     prior year (e.g. a failed-then-retried posting).  We reset it here
    #     so that _calculate_default_accounting_date (overridden above) is
    #     called fresh, ensuring the correct year is used in the sequence.
    #     """
    #     today = fields.Date.context_today(self)
    #     year_start = date_utils.start_of(today, 'year')
    #     for sheet in self:
    #         if sheet.accounting_date and sheet.accounting_date < year_start:
    #             sheet.sudo().accounting_date = False
    #     return super()._do_create_moves()

    def _prepare_bills_vals(self):
        """Override to force sequence recalculation for current year"""
        self.ensure_one()
        move_vals = self._prepare_move_vals()
        if self.employee_id.sudo().bank_account_id:
            move_vals['partner_bank_id'] = self.employee_id.sudo().bank_account_id.id
        
        result = {
            **move_vals,
            'journal_id': self.journal_id.id,
            'ref': self.name,
            'move_type': 'in_invoice',
            'partner_id': self.employee_id.sudo().work_contact_id.id,
            'commercial_partner_id': self.employee_id.user_partner_id.id,
            'currency_id': self.currency_id.id,
            'line_ids': [Command.create(expense._prepare_move_lines_vals()) for expense in self.expense_line_ids],
            'attachment_ids': [
                Command.create(attachment.copy_data({'res_model': 'account.move', 'res_id': False, 'raw': attachment.raw})[0])
                for attachment in self.expense_line_ids.message_main_attachment_id
            ],
        }
        
        # Force sequence recalculation for General Vendors Bills to avoid date mismatch
        if self.journal_id and 'General Vendors Bills' in self.journal_id.name:
            result['name'] = '/'
            # Ensure the date is set to current date for proper sequence generation
            result['date'] = fields.Date.context_today(self)
            
        return result

    def _do_create_moves(self):
        """Override to handle sequence date mismatch for General Vendors Bills"""
        # Temporarily bypass sequence validation for General Vendors Bills
        if self.journal_id and 'General Vendors Bills' in self.journal_id.name:
            # Set context to bypass sequence validation
            self = self.with_context(bypass_sequence_validation=True)
        
        return super()._do_create_moves()

    def action_open_all_attachments(self):
        self.ensure_one()
        attachments = self.env['ir.attachment'].search([
            ('res_model', '=', 'hr.expense'),
            ('res_id', 'in', self.expense_line_ids.ids),
        ])
        return {
            'type': 'ir.actions.act_window',
            'name': 'Documents',
            'res_model': 'ir.attachment',
            'view_mode': 'kanban,list,form',
            'domain': [('id', 'in', attachments.ids)],
            'context': {
                'default_res_model': 'hr.expense',
            },
            'target': 'current',
        }
