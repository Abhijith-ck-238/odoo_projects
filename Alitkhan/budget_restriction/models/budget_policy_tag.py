# -*- coding: utf-8 -*-
from odoo import models, fields


class BudgetPolicyTag(models.Model):
    """Custom Tag Model - can be used for categorization"""
    _name = 'budget.policy.tag'
    _description = 'Budget Policy Tag'
    _order = 'name'

    name = fields.Char(
        string='Tag Name',
        required=True,
        translate=True,
        index=True
    )
    color = fields.Integer(
        string='Color',
        default=0,
        help='Color index for tag display'
    )
