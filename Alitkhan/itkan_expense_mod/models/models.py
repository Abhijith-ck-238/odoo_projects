# -*- coding: utf-8 -*-

from odoo import models, fields, api


class HrExpenseSheetExtension(models.Model):
    
    _inherit = "hr.expense.sheet"


    total_iqd_amounts = fields.Float(string="Total IQDs",compute="compute_total_iqd")
    total_usd_amounts = fields.Float(string="Total USDs",compute="compute_total_usd")
    

    def compute_total_iqd(self):
        for rcd in self:
            total_iqds = self.env["hr.expense"].search([("currency_id.name","=","IQD"),("sheet_id","=",rcd.id)])
            iqd_rate = self.env["res.currency"].search([('name',"=","IQD")]).rate
            if total_iqds:
                rcd.total_iqd_amounts = sum([item.total_amount_currency for item in total_iqds])
            else:
                rcd.total_iqd_amounts = 0
    def compute_total_usd(self):
        for rcd in self:
            total_usds = self.env["hr.expense"].search([("currency_id.name","=","USD"),("sheet_id","=",rcd.id)])
            if total_usds:
                rcd.total_usd_amounts = sum([item.total_amount for item in total_usds])
            else:
                rcd.total_usd_amounts = 0
            