# -*- coding: utf-8 -*-

from odoo import models, fields, api


class Contract(models.Model):
    _inherit = 'contract.contract'

    @api.model
    def get_invisible_attachment_ids(self, record_id):
        """ Used to Fetch the financial_docs_att data """
        record = self.env['contract.contract'].sudo().browse(record_id)
        if record.exists():
            return record.financial_docs_att.ids
        return []