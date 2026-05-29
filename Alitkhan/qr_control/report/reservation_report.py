# -*- coding: utf-8 -*-

from odoo import tools
from odoo import api, fields, models


class ReservationReport(models.Model):
    _name = "reservation.report"
    _description = "Reservations Analysis Report"
    _auto = False
    _rec_name = 'date'
    _order = 'date desc'

    name = fields.Char('Reservation Reference', readonly=True)
    date = fields.Datetime('Reservation Date', readonly=True)
    product_id = fields.Many2one('product.product', 'Product', readonly=True)
    qty_reserved = fields.Float('Qty Reserved', readonly=True)
    partner_id = fields.Many2one('res.partner', 'Customer', readonly=True)
    company_id = fields.Many2one('res.company', 'Company', readonly=True)
    user_id = fields.Many2one('res.users', 'Salesperson', readonly=True)
    nbr = fields.Integer('# of Lines', readonly=True)
    state = fields.Selection([
        ('draft', 'Draft Quotation'),
        ('done', 'Sales Done'),
    ], string='Status', readonly=True)
    reserved_product_id = fields.Many2one('reserved.product', 'Reservation #', readonly=True)

    def init(self):
        tools.drop_view_if_exists(self.env.cr, "reservation_report")
        self.env.cr.execute("""CREATE or REPLACE VIEW reservation_report as (
        SELECT
            min(rl.id) as id,
            rl.product_id as product_id,
            rl.qty_reserved as qty_reserved,
            count(*) as nbr,
            r.name as name,
            r.date as date,
            r.user_id as user_id,
            r.state as state,
            r.reserved_partner_id as partner_id,
            r.company_id as company_id,
            r.id as reserved_product_id
        FROM
               reserved_product_line rl
        JOIN
               reserved_product r on (rl.reserved_product_id=r.id)
        WHERE
               rl.product_id IS NOT NULL 
        GROUP BY
            rl.product_id,
            rl.reserved_product_id,
            rl.qty_reserved,
            r.name,
            r.date,
            r.reserved_partner_id,
            r.user_id,
            r.state,
            r.company_id,
            r.id
        
        )""")
