from odoo import models, fields


class CustomPlanningSlot(models.Model):
    _name = 'planning.slot'
    _inherit = ['planning.slot', 'mail.thread', 'mail.activity.mixin']

    planning_id = fields.Many2one(
        'planning.planning',
        string='Planning',
        ondelete='cascade'
    )

    is_published = fields.Boolean("Is the shift sent", default=False,
                                  readonly=True,
                                  help="If checked, this means the planning entry has been sent to the employee. Modifying the planning entry will mark it as not sent.")

    def action_send(self):
        group_planning_user = self.env.ref('planning.group_planning_user')
        template = self.env.ref('planning.email_template_slot_single')
        view_context = dict(self._context)
        view_context.update({
            'menu_id': str(self.env.ref('planning.planning_menu_root').id),
            'action_id': str(
                self.env.ref('planning.planning_action_open_shift').id),
            'dbname': self.env.cr.dbname,
            'render_link': self.employee_id.user_id and self.employee_id.user_id in group_planning_user.users,
            'unavailable_path': '/planning/myshifts/',
        })
        slot_template = template.with_context(view_context)

        mails_to_send = self.env['mail.mail']
        for slot in self:
            if slot.employee_id and slot.employee_id.work_email:
                mail_id = slot_template.with_context(view_context).send_mail(
                    slot.id, email_layout_xmlid='mail.mail_notification_light')

                current_mail = self.env['mail.mail'].browse(mail_id)
                mails_to_send |= current_mail

            if slot.employee_id.user_id:
                note = _("The planning schedule sent.")
                slot.activity_schedule(
                    'custom_planning.mail_activity_send_schedule',
                    note=note,
                    user_id=slot.employee_id.user_id.id)

        if mails_to_send:
            mails_to_send.send()

        self.write({
            'is_published': True,
            'publication_warning': False,
        })
        return mails_to_send
    