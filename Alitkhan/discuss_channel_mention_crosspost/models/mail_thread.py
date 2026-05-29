import logging
import re
from markupsafe import Markup

from odoo import models, api

_logger = logging.getLogger(__name__)


class MailThread(models.AbstractModel):
    _inherit = 'mail.thread'

    @api.model
    def _extract_channel_ids_from_body(self, body):
        """
        Extract channel IDs from mentions like:
        <a href="#" class="o_mail_redirect" data-oe-id="2" data-oe-model="discuss.channel" target="_blank">#general</a>
        """
        if not body:
            return []
        # Find all data-oe-id for elements where data-oe-model="discuss.channel"
        # Since HTML attributes can be in any order, we do a relaxed search
        regex = r'<a[^>]+data-oe-model=["\']discuss\.channel["\'][^>]+data-oe-id=["\'](\d+)["\'][^>]*>'
        matches = re.finditer(regex, body)
        channel_ids = [int(match.group(1)) for match in matches]

        # Also handle cases where data-oe-id might come before data-oe-model
        regex_alt = r'<a[^>]+data-oe-id=["\'](\d+)["\'][^>]+data-oe-model=["\']discuss\.channel["\'][^>]*>'
        matches_alt = re.finditer(regex_alt, body)
        channel_ids.extend([int(match.group(1)) for match in matches_alt])

        return list(set(channel_ids))

    def _message_post_after_hook(self, message, msg_vals):
        res = super(MailThread, self)._message_post_after_hook(message, msg_vals)

        # Skip if message is already posted on a channel directly to prevent loops
        if self._name == 'discuss.channel':
            return res

        # Skip system messages like "Task created" unless they also have explicit body mentions
        # We generally only want to crosspost actual user comments
        if msg_vals.get('message_type') != 'comment':
            return res

        body = message.body
        channel_ids = self._extract_channel_ids_from_body(body)

        if channel_ids:
            channels = self.env['discuss.channel'].sudo().browse(channel_ids).exists()

            # Format a prefix to link back to the original document
            document_name = self.display_name or 'a document'
            model_description = self.env['ir.model']._get(self._name).display_name or self._name
            original_url = f"/odoo/{self._name}/{self.id}"

            prefix = f'<p><em>Message posted from <a href="{original_url}">{model_description}: {document_name}</a></em></p>'
            new_body = Markup(prefix) + (Markup(body) if not isinstance(body, Markup) else body)

            for channel in channels:
                # If configured, send email by notifying directly the channel members
                partner_ids = []
                if channel.crosspost_send_email:
                    # Get all partner ids for the members of this channel
                    partner_ids = channel.channel_member_ids.mapped('partner_id.id')

                # Post the message in the channel (This doesn't send emails due to Odoo channel restrictions)
                channel.with_context(mail_post_autofollow=False).message_post(
                    body=new_body,
                    message_type='comment',
                    subtype_xmlid='mail.mt_comment',
                    author_id=message.author_id.id,
                    attachment_ids=message.attachment_ids.ids,
                )

                # Send an explicit notification (email) to the members from the original record
                if partner_ids:
                    partners = self.env['res.partner'].sudo().browse(partner_ids)
                    mails_to = []
                    for partner in partners:
                        if partner.email:
                            mails_to.append(partner.email)
                    mail = self.env['mail.mail'].sudo().create({
                        'subject': f"Notification: {model_description} {document_name}",
                        'body_html': new_body,
                        'email_to': ','.join(mails_to),
                        'email_from': message.author_id.email_formatted or self.env.company.catchall_formatted,
                        'author_id': message.author_id.id,
                        'auto_delete': False,
                    })
                    mail.send()

        return res
