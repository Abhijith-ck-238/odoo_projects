from odoo import models,_
from odoo.exceptions import ValidationError

class IrAttachment(models.Model):
    _inherit = 'ir.attachment'

    def unlink(self):
        if self.env.user.has_group('account.group_account_manager'):
            return super().unlink()

        restricted_states = {
            'hr.expense.sheet': ('post', 'done'),
            'hr.expense': ('approved', 'done'),
        }

        for attachment in self:
            model = attachment.res_model
            states = restricted_states.get(model)

            if not states:
                continue

            record = self.env[model].browse(attachment.res_id)

            if record.exists() and record.state in states:
                raise ValidationError(_('You cannot delete attachments'))

        return super().unlink()
