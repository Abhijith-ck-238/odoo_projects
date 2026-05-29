# -*- coding: utf-8 -*-
from odoo import fields, models


class IrActionsActWindowView(models.Model):
    """Dashboard Action Window View Model"""
    _inherit = 'ir.actions.act_window.view'

    active = fields.Boolean(
        'Active', default=True)
    # view_mode = fields.Selection(selection_add=[("studio_search", "Studio Search")], ondelete={"studio_search": "cascade"})
