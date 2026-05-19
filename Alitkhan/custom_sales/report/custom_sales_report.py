from odoo import models, fields, api
from odoo.http import request
from odoo import tools


class CustomSaleReport(models.Model):
    _inherit = 'sale.report'

    teams = fields.Many2one('crm.team', string="Choose sale teams",
                            readonly=True)
    total_exchange = fields.Float(string="Total Exchange Value", readonly=True)
    total_usd_price = fields.Float(string="Total USD", readonly=True)
    total_iqd_price = fields.Float(string="Total IQD", readonly=True)
    total_eur_price = fields.Float(string="Total EUR", readonly=True)
    untaxed_total_usd_price = fields.Float(string="Untaxed Total USD",
                                           readonly=True)
    untaxed_total_iqd_price = fields.Float(string="Untaxed Total IQD",
                                           readonly=True)
    untaxed_total_eur_price = fields.Float(string="Untaxed Total EUR",
                                           readonly=True)

    def _select_sale(self):
        # Call the parent method to get the base select clause
        select_ = super()._select_sale()

        # Extend the select clause with additional fields
        additional_select = f""",
            COALESCE(SUM(CASE WHEN l.is_exchange IS TRUE AND s.state IN ('sale', 'done') 
                THEN l.price_subtotal ELSE 0 END), 0) AS total_exchange,
            COALESCE(SUM(CASE WHEN pp.currency_id = 2 
                THEN l.price_total ELSE 0 END), 0) AS total_usd_price,
            COALESCE(SUM(CASE WHEN pp.currency_id = 90 
                THEN l.price_total ELSE 0 END), 0) AS total_iqd_price,
            COALESCE(SUM(CASE WHEN pp.currency_id = 1 
                THEN l.price_total ELSE 0 END), 0) AS total_eur_price,
            COALESCE(SUM(CASE WHEN pp.currency_id = 2 
                THEN l.untaxed_amount_to_invoice ELSE 0 END), 0) AS untaxed_total_usd_price,
            COALESCE(SUM(CASE WHEN pp.currency_id = 90 
                THEN l.untaxed_amount_to_invoice ELSE 0 END), 0) AS untaxed_total_iqd_price,
            COALESCE(SUM(CASE WHEN pp.currency_id = 1 
                THEN l.untaxed_amount_to_invoice ELSE 0 END), 0) AS untaxed_total_eur_price"""

        return select_ + additional_select

    def _from_sale(self):
        # Call the parent method to get the base from clause
        from_ = super()._from_sale()

        # Add product pricelist join
        from_ += """
            LEFT JOIN product_pricelist pp ON s.pricelist_id = pp.id
        """
        return from_

    def _where_sale(self):
        # Modify where clause to exclude expense categories
        base_where = super()._where_sale()
        return f"""{base_where} AND (t.categ_id IS NULL OR t.categ_id NOT IN (
            SELECT id FROM product_category WHERE name LIKE '%Expense%'
        ))"""

    def _group_by_sale(self):
        # Call the parent method to get the base group by clause
        group_by = super()._group_by_sale()

        # Add additional grouping for pricelist currency
        group_by += ", pp.currency_id"
        return group_by

    def init(self):
        # Initialize the view when the model is loaded
        tools.drop_view_if_exists(self.env.cr, self._table)
        self.env.cr.execute(f"""
            CREATE OR REPLACE VIEW {self._table} AS (
                {self._query()}
            )
        """)

    def render_report(self):
        try:
            tools.drop_view_if_exists(self.env.cr, self._table)
            self.env.cr.execute("""CREATE or REPLACE VIEW %s as (%s)""" % (
                self._table, self._query()))
            action = self.env.ref('website_sale.sale_report_action_dashboard').read()[0]
            return action
        except:
            pass