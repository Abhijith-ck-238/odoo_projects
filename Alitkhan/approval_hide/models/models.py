# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError

class ApprovalCategoryExt(models.Model):

    _inherit = "approval.category"

    apply_limitations = fields.Boolean(string="Apply Access Limitations",help="Check this option to enable access limitations on this record")
    accessible_to_ids = fields.Many2many("res.users","approval_id",string="Accessible to")
