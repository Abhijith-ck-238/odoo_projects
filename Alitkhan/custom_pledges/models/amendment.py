from odoo import fields, models


class Amendments(models.Model):
    """ Amendments"""
    _name = 'amendment.amendment'
    _description = 'Amendments'

    description = fields.Char(string="Description")
    status = fields.Selection([
        ('pending', "Pending"),
        ('done', "Done"),
        ('refused', "Refused")
    ], string="Status")
    pledge_id = fields.Many2one('pledge.pledge')

    def send_amendment_notification(self):
        """ Method to send mail to Accounting user groups about the pending amendments."""
        res = self.env['pledge.pledge'].search(
            [('lca_type', '=', 'letter of credit'),
             ('count_pending_amendments', '>', 0)])
        action_id = self.env.ref(
            'pledge_assets.pledge_window').id
        base_url = self.env['ir.config_parameter'].sudo().get_param(
            'web.base.url')
        pledges = []
        for rec in res:
            val = {
                'contract': rec.related_contract.name,
                'iq': rec.related_contract.iq,
                'url': f'{base_url}/web#id={rec.id}&action={action_id}&model=pledge.pledge&view_type=form',
                'pledge_name': rec.name,
                'pending_amendments': rec.count_pending_amendments,
            }
            pledges.append(val)
        super_user = self.env['res.users'].browse(1)
        users = []
        group_id = self.env.ref('account.group_account_user')
        for recepient in group_id.users:
            users.append(recepient.partner_id.id)

        mail_values = {
            'email_from': super_user.partner_id.email,
            'subject': 'Amendment Reminder',
            'email_to': ','.join([p.partner_id.email for p in group_id.users]),
        }

        template = self.env.ref(
            'custom_pledges.mail_template_amendment_reminder')
        template.with_context(pledges=pledges).send_mail(
            super_user.id,
            email_values=mail_values,
            force_send=True
        )
