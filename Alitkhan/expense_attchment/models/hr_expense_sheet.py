from odoo import models, api, fields


class HrExpenseSheet(models.Model):
    _inherit = "hr.expense.sheet"

    nb_attachment = fields.Integer(string="Number of Attachments",
                                   compute='_compute_nb_attachment')

    @api.depends('expense_line_ids.attachment_ids')
    def _compute_nb_attachment(self):
        for sheet in self:
            # Collect all attachments linked to all expense lines in the sheet
            attachments = sheet.expense_line_ids.mapped('attachment_ids')
            sheet.nb_attachment = len(attachments)

    @api.onchange('analytic_account_id')
    def _onchange_analytic_account_id(self):
        self.journal_id = self.analytic_account_id.journal_id.id

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
            'context': {'default_res_model': 'hr.expense.sheet',
                        'default_res_id': self.id},
            'target': 'current',
        }
