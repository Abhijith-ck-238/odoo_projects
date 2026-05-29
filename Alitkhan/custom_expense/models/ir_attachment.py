from odoo import models, _
from odoo.exceptions import UserError


class IrAttachment(models.Model):
    _inherit = 'ir.attachment'

    def unlink(self):
        """
        Block deletion of attachments linked to hr.expense or hr.expense.sheet
        records that are in 'posted' or 'done' state.
        """
        LOCKED_STATES = {'post', 'done'}

        # Check attachments linked to hr.expense.sheet (expense reports)
        sheet_attachments = self.filtered(
            lambda a: a.res_model == 'hr.expense.sheet' and a.res_id
        )
        if sheet_attachments:
            sheet_ids = sheet_attachments.mapped('res_id')
            locked_sheets = self.env['hr.expense.sheet'].sudo().search([
                ('id', 'in', sheet_ids),
                ('state', 'in', list(LOCKED_STATES)),
            ])
            if locked_sheets:
                raise UserError(_(
                    "You cannot delete attachments from expense reports that are "
                    "in 'Posted' or 'Done' state.\n\n"
                    "Affected expense report(s): %s"
                ) % ', '.join(locked_sheets.mapped('name')))

        return super().unlink()
