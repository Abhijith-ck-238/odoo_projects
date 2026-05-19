# -*- coding: utf-8 -*-

from odoo import tools
from odoo import api, fields, models


class PledgeReport(models.Model):
    _name = "pledge.report"
    _description = "Pledge Analysis Report"
    _auto = False
    _rec_name = 'date'
    _order = 'date desc'
    
    name = fields.Char('Pledge Reference', readonly=True)
    date = fields.Datetime('Pledge Acceptance Date', readonly=True)
    pledge_type = fields.Selection(selection=[('bid bond', 'Bid Bond'),
                                              ('performance bond', 'Performance Bond'),
                                              ('letter of credit', 'Letter of Credit')])
    currency_id = fields.Many2one('res.currency', string="Currency")
    amount = fields.Float(string="Amount")
    status = fields.Selection(string="Status",selection=[('draft', 'Draft'),
                                                         ('confirmed', 'Confirmed'),
                                                         ('expired', 'Expired'),
                                                         ('cleared', 'Cleared')])
    pending_amendments = fields.Integer(string="Pending Amendments")
    contract_type = fields.Selection(
        selection=[('supplying_and_maintenance', 'Supplying & Maintenance'),
                   ('maintenance', 'Maintenance'),
                   ('supplying', 'Supplying'),
                   ('3rd_party', '3rd Party'),
                   ('demo', 'Demo'),
                   ('n.a', 'N.A'),
                   ('other', 'Other'),
                   ('installation_only', 'Installation Only')],
        string="Contract Type")
    amount_coverage = fields.Float(string="Amount Coverage")
    paid_amount = fields.Float(string="Paid Amount")
    opining_date = fields.Date(string="Opining Date")
    expire_date = fields.Date(string="Expire Date")
    date_of_extension = fields.Date(string="Date of Extension")
    total_pending_amendments = fields.Integer(string="Total Pending Amendments")
    total_iqd_amount = fields.Float(string="Total IQD Amount")
    total_eur_amount = fields.Float(string="Total EUR Amount")
    total_usd_amount = fields.Float(string="Total USD Amount")
    total_iqd_paid_amount = fields.Float(string="Total IQD Paid Amount")
    total_eur_paid_amount = fields.Float(string="Total EUR Paid Amount")
    total_usd_paid_amount = fields.Float(string="Total USD Paid Amount")
    total_iqd_amount_coverage = fields.Float(string="Total IQD Amount Coverage")
    total_eur_amount_coverage = fields.Float(string="Total EUR Amount Coverage")
    total_usd_amount_coverage = fields.Float(string="Total USD Amount Coverage")
    total_bid_bond_iqd_amount = fields.Float(string="Total Bid Bond IQD Amount")
    total_bid_bond_eur_amount = fields.Float(string="Total Bid Bond EUR Amount")
    total_bid_bond_usd_amount = fields.Float(string="Total Bid Bond USD Amount")
    total_performance_bond_iqd_amount = fields.Float(string="Total Performance Bond IQD Amount")
    total_performance_bond_eur_amount = fields.Float(string="Total Performance Bond EUR Amount")
    total_performance_bond_usd_amount = fields.Float(string="Total Performance Bond USD Amount")
    total_letter_of_credit_iqd_amount = fields.Float(string="Total Letter of Credit IQD Amount")
    total_letter_of_credit_eur_amount = fields.Float(string="Total Letter of Credit EUR Amount")
    total_letter_of_credit_usd_amount = fields.Float(string="Total Letter of Credit USD Amount")
    cleared_total_amount_iqd = fields.Float(string="Cleared Total IQD Amount")
    cleared_total_amount_eur = fields.Float(string="Cleared Total EUR Amount")
    cleared_total_amount_usd = fields.Float(string="Cleared Total USD Amount")
    uncleared_total_amount_iqd = fields.Float(string="Uncleared Total IQD Amount")
    uncleared_total_amount_eur = fields.Float(string="Uncleared Total EUR Amount")
    uncleared_total_amount_usd = fields.Float(string="Uncleared Total USD Amount")

    def init(self):
        tools.drop_view_if_exists(self.env.cr, 'pledge_report')
        self.env.cr.execute("""
               CREATE or REPLACE VIEW pledge_report AS (
                   SELECT
                       min(r.id) as id,
                       r.name as name,
                       r.acceptance_date as date,
                       r.lca_type as pledge_type,
                       r.currency_id as currency_id,
                       r.amount as amount,
                       r.status as status,
                       r.count_pending_amendments as pending_amendments,
                       r.contract_type as contract_type,
                       0.0 as amount_coverage,  /* Default value of 0.0 */
                       r.paid_amount as paid_amount,
                       r.date_of_extension as date_of_extension,
                       sum(r.count_pending_amendments) as total_pending_amendments,
                       sum(CASE WHEN r.currency_id = 90 THEN (r.amount / CASE COALESCE(r.currency_rate, 0) WHEN 0 THEN 1.0 ELSE r.currency_rate END) ELSE 0 END) as total_iqd_amount,
                       sum(CASE WHEN r.currency_id = 1 THEN (r.amount / CASE COALESCE(r.currency_rate, 0) WHEN 0 THEN 1.0 ELSE r.currency_rate END) ELSE 0 END) as total_eur_amount,
                       sum(CASE WHEN r.currency_id = 2 THEN (r.amount / CASE COALESCE(r.currency_rate, 0) WHEN 0 THEN 1.0 ELSE r.currency_rate END) ELSE 0 END) as total_usd_amount,
                       sum(CASE WHEN r.currency_id = 90 THEN (r.paid_amount / CASE COALESCE(r.currency_rate, 0) WHEN 0 THEN 1.0 ELSE r.currency_rate END) ELSE 0 END) as total_iqd_paid_amount,
                       sum(CASE WHEN r.currency_id = 1 THEN (r.paid_amount / CASE COALESCE(r.currency_rate, 0) WHEN 0 THEN 1.0 ELSE r.currency_rate END) ELSE 0 END) as total_eur_paid_amount,
                       sum(CASE WHEN r.currency_id = 2 THEN (r.paid_amount / CASE COALESCE(r.currency_rate, 0) WHEN 0 THEN 1.0 ELSE r.currency_rate END) ELSE 0 END) as total_usd_paid_amount,
                       0.0 as total_iqd_amount_coverage,  /* Default value of 0.0 */
                       0.0 as total_eur_amount_coverage,  /* Default value of 0.0 */
                       0.0 as total_usd_amount_coverage,  /* Default value of 0.0 */
                       sum(CASE WHEN r.lca_type = 'bid bond' AND r.currency_id = 90 THEN (r.amount / CASE COALESCE(r.currency_rate, 0) WHEN 0 THEN 1.0 ELSE r.currency_rate END) ELSE 0 END) as total_bid_bond_iqd_amount,
                       sum(CASE WHEN r.lca_type = 'bid bond' AND r.currency_id = 1 THEN (r.amount / CASE COALESCE(r.currency_rate, 0) WHEN 0 THEN 1.0 ELSE r.currency_rate END) ELSE 0 END) as total_bid_bond_eur_amount,
                       sum(CASE WHEN r.lca_type = 'bid bond' AND r.currency_id = 2 THEN (r.amount / CASE COALESCE(r.currency_rate, 0) WHEN 0 THEN 1.0 ELSE r.currency_rate END) ELSE 0 END) as total_bid_bond_usd_amount,
                       sum(CASE WHEN r.lca_type = 'performance bond' AND r.currency_id = 90 THEN (r.amount / CASE COALESCE(r.currency_rate, 0) WHEN 0 THEN 1.0 ELSE r.currency_rate END) ELSE 0 END) as total_performance_bond_iqd_amount,
                       sum(CASE WHEN r.lca_type = 'performance bond' AND r.currency_id = 1 THEN (r.amount / CASE COALESCE(r.currency_rate, 0) WHEN 0 THEN 1.0 ELSE r.currency_rate END) ELSE 0 END) as total_performance_bond_eur_amount,
                       sum(CASE WHEN r.lca_type = 'performance bond' AND r.currency_id = 2 THEN (r.amount / CASE COALESCE(r.currency_rate, 0) WHEN 0 THEN 1.0 ELSE r.currency_rate END) ELSE 0 END) as total_performance_bond_usd_amount,
                       sum(CASE WHEN r.lca_type = 'letter of credit' AND r.currency_id = 90 THEN (r.amount / CASE COALESCE(r.currency_rate, 0) WHEN 0 THEN 1.0 ELSE r.currency_rate END) ELSE 0 END) as total_letter_of_credit_iqd_amount,
                       sum(CASE WHEN r.lca_type = 'letter of credit' AND r.currency_id = 1 THEN (r.amount / CASE COALESCE(r.currency_rate, 0) WHEN 0 THEN 1.0 ELSE r.currency_rate END) ELSE 0 END) as total_letter_of_credit_eur_amount,
                       sum(CASE WHEN r.lca_type = 'letter of credit' AND r.currency_id = 2 THEN (r.amount / CASE COALESCE(r.currency_rate, 0) WHEN 0 THEN 1.0 ELSE r.currency_rate END) ELSE 0 END) as total_letter_of_credit_usd_amount,
                       sum(CASE WHEN r.status = 'cleared' AND r.currency_id = 90 THEN (r.amount / CASE COALESCE(r.currency_rate, 0) WHEN 0 THEN 1.0 ELSE r.currency_rate END) ELSE 0 END) as cleared_total_amount_iqd,
                       sum(CASE WHEN r.status = 'cleared' AND r.currency_id = 1 THEN (r.amount / CASE COALESCE(r.currency_rate, 0) WHEN 0 THEN 1.0 ELSE r.currency_rate END) ELSE 0 END) as cleared_total_amount_eur,
                       sum(CASE WHEN r.status = 'cleared' AND r.currency_id = 2 THEN (r.amount / CASE COALESCE(r.currency_rate, 0) WHEN 0 THEN 1.0 ELSE r.currency_rate END) ELSE 0 END) as cleared_total_amount_usd,
                       sum(CASE WHEN r.status != 'cleared' AND r.currency_id = 90 THEN (r.amount / CASE COALESCE(r.currency_rate, 0) WHEN 0 THEN 1.0 ELSE r.currency_rate END) ELSE 0 END) as uncleared_total_amount_iqd,
                       sum(CASE WHEN r.status != 'cleared' AND r.currency_id = 1 THEN (r.amount / CASE COALESCE(r.currency_rate, 0) WHEN 0 THEN 1.0 ELSE r.currency_rate END) ELSE 0 END) as uncleared_total_amount_eur,
                       sum(CASE WHEN r.status != 'cleared' AND r.currency_id = 2 THEN (r.amount / CASE COALESCE(r.currency_rate, 0) WHEN 0 THEN 1.0 ELSE r.currency_rate END) ELSE 0 END) as uncleared_total_amount_usd
                   FROM
                       pledge_pledge r
                   GROUP BY
                       r.name,
                       r.lca_type,
                       r.acceptance_date,
                       r.currency_id,
                       r.amount,
                       r.status,
                       r.count_pending_amendments,
                       r.contract_type,
                       r.paid_amount,
                       r.date_of_extension
               )
           """)
