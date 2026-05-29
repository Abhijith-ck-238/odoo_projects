# -*- coding: utf-8 -*-
import logging
from odoo import models
_logger = logging.getLogger('odoo.tests.test_module_operations')



class Contract(models.Model):
    _inherit = "contract.contract"

    def set_attachment_data(self):
        """set the res_id to all the attachments inside the attachment's
         fields of contract and contract product models"""
        self.env.cr.execute('''
            UPDATE ir_attachment 
            SET res_id = rel.contract_id,
                res_model = 'contract.contract'
            FROM attachement_contracts_docs_rel rel
            WHERE ir_attachment.id = rel.attachment_id
            AND (ir_attachment.res_id != rel.contract_id OR ir_attachment.res_id IS NULL)
        ''')
        self.env.cr.execute('''
            UPDATE ir_attachment 
            SET res_id = rel.contract_line_id,
                res_model = 'contract.product'
            FROM attachment_contract_line_pac_document_rel rel
            WHERE ir_attachment.id = rel.attachment_id
            AND (ir_attachment.res_id != rel.contract_line_id OR ir_attachment.res_id IS NULL)
        ''')

    @api.model
    def fix_helpdesk_attachment_res_id(self):
        contracts = self.search([])
        Attachment = self.env['ir.attachment']
        count = 0
        for contract in contracts:
            attachments = (contract.technical_docs_att | contract.financial_docs_att| contract.attachements)

            attachments_to_fix = attachments.filtered(
                lambda att: not att.res_id or att.res_id == 0
            )
            count += len(attachments_to_fix)

            if attachments_to_fix:
                attachments_to_fix.write({
                    'res_id': contract.id,
                    'res_model': contract._name,
                })
            _logger.info("Fixed %s helpdesk attachments", count)
