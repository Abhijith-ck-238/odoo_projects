# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError
import datetime

class MailThread(models.AbstractModel):
	_inherit = 'mail.thread'

	def _message_auto_subscribe_followers(self, updated_values, default_subtype_ids):
		field = self._fields.get('user_id')
		if 'helpdesk.ticket' in str(field):
			return []
		else:
			return super(MailThread, self)._message_auto_subscribe_followers(updated_values=updated_values, default_subtype_ids=default_subtype_ids)