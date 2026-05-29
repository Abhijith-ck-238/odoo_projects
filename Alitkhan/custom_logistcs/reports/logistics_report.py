from odoo import fields, models, tools


class LogisticsReport(models.Model):
    _name = "logistics.report"
    _description = "Logistics Analysis Report"
    _auto = False

    shipment_id = fields.Many2one('logistics.shipment', 'Shipment', readonly=True)
    status = fields.Selection(selection=[('draft', 'Draft'),('active', 'Active'),('done', 'Done')], string='Status', readonly=True)
    contract_id = fields.Many2one('contract.contract', "Contract", readonly=True)
    purchase_id = fields.Many2one('purchase.order', "Purchase Order", readonly=True)
    shipment_value = fields.Float("Shipment Value", readonly=True)
    purchase_total = fields.Float("Purchase Total", readonly=True)
    fees_percentage = fields.Float("Fess Percentage", readonly=True)
    bill_total = fields.Float("Bill Total", readonly=True)
    create_date = fields.Date("Create Date")

    def init(self):
        tools.drop_view_if_exists(self.env.cr, "logistics_report")
        self.env.cr.execute("""CREATE or REPLACE VIEW logistics_report as (
        SELECT
            min(rl.id) as id,
            rl.id as shipment_id,
            rl.status as status,
            r.col2 as contract_id,
            p.col2 as purchase_id,
            sum(rl.shipment_value) as shipment_value,
            sum(rl.purchase_total_stored) as purchase_total,
            sum(rl.fees_percentage_stored) as fees_percentage,
            sum(rl.bill_total_stored) as bill_total,
            rl.create_date as create_date
            
        FROM
            logistics_shipment rl
        LEFT JOIN
            shipment_contracts r on rl.id = r.col1  
        LEFT JOIN
            shipment_purchase p on rl.id = p.col1
        GROUP BY
            rl.id,
            rl.status,
            r.col2,
            p.col2,
            rl.create_date
        )""")
