# -*- coding: utf-8 -*-

from odoo import models, fields, api


class AccountMove(models.Model):
    _inherit="account.move"
    
    contract_id = fields.Many2one("contract.contract",'Contract')
    contract_category = fields.Selection([("private","Private"),("governmental","Governmental")],'Contract Category')

class ContractContractExt(models.Model):
    _inherit="contract.contract"


    def redirect_to_invoices(self,context={}):
        form_view_id = self.env.ref("account.view_move_form").id
        tree_view_id = self.env.ref("account.view_invoice_tree").id
        context.update({"default_contract_id":self.id,
                        "default_contract_category":self.contract_categ})
        return {
            'type': 'ir.actions.act_window',
            'name': 'Invoices',
            'view_type': ['form','list','pivot','graph'],
            'view_mode': 'list',
            'res_model': 'account.move',
            'views': [(tree_view_id,'list'),(form_view_id, 'form'),(False,'pivot'),(False,'graph')],
            'domain': [('contract_id', '=', self.id)],
            'target': 'current',
            'context':context,   
                       
        }

class HrExpenseSheet(models.Model):

    _inherit = "hr.expense.sheet"

    contract_id = fields.Many2one("contract.contract",string="Related Contract")

    
    @api.constrains("account_move_ids")
    def _relate_expense_journal(self):
        for rcd in self:
            rcd.account_move_ids.write({
                'contract_id' : rcd.contract_id,
            })
            # rcd.account_move_ids.contract_id = rcd.contract_id
