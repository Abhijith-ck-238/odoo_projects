# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError


class ApprovalCategoriesExt(models.Model):
    _inherit = "approval.category"

    carbon_copy_ids = fields.Many2many(comodel_name="res.partner", relation="user_approval_rel",
                                       column1="user_approval", column2="approval_user", string="CC")


class ApprovalRequestExt(models.Model):
    _inherit = "approval.request"

    def action_confirm(self):
        res = super(ApprovalRequestExt, self).action_confirm()
        self.message_post(
            body="%s has submitted a %s request" % (self.request_owner_id.name, self.name),
            message_type='notification',
            subtype_xmlid='mail.mt_comment',
            partner_ids=[user_id.id for user_id in self.category_id.carbon_copy_ids]  # The users you want to notify
        )
        return res
