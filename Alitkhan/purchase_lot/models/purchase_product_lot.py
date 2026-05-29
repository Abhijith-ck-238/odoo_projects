# -*- coding: utf-8 -*-

from odoo import models, fields, api


class PurchaseProductLot(models.Model):
    _name = 'purchase.product.lot'
    _description = "Purchase Product Lot/Serial"
    _rec_name = 'name'
    _order = 'name, id'

    name = fields.Char('Lot/Serial Number', required=True, help="Unique Lot/Serial Number")
    ref = fields.Char('Internal Reference',
                      help="Internal reference number in case it differs from the manufacturer's lot/serial number")
    po_line_id = fields.Many2one('purchase.order.line')
    product_id = fields.Many2one(
        'product.product', 'Product', related='po_line_id.product_id',
        domain=lambda self: self._domain_product_id(), required=True, check_company=True)
    product_uom_id = fields.Many2one(
        'uom.uom', 'Unit of Measure',
        related='product_id.uom_id', store=True, readonly=False)
    product_qty = fields.Float('Quantity',)
    note = fields.Html(string='Description')
    company_id = fields.Many2one('res.company', 'Company', default=lambda self: self.env.company,
                                 required=True, stored=True, index=True)
    lot_id = fields.Many2one('stock.lot', string="Lot/Serial")
    use_date = fields.Datetime(string='Best before Date',
                               help='This is the date on which the goods with this Serial Number start '
                                    'deteriorating, without being dangerous yet.')
    alert_date = fields.Datetime(string='Alert Date', compute='_compute_alert_date',
                                 help='Date to determine the expired lots and serial numbers using '
                                      'the filter "Expiration Alerts".')

    _sql_constraints = [
        ('name_ref_uniq', 'unique (name, product_id, company_id)',
         'The combination of serial number and product must be unique across a company !'),
    ]

    def _domain_product_id(self):
        domain = [
            "('tracking', '!=', 'none')",
            "('type', '=', 'consu')",
            "'|'",
                "('company_id', '=', False)",
                "('company_id', '=', company_id)"
        ]
        return '[' + ', '.join(domain) + ']'

    @api.depends('use_date')
    def _compute_alert_date(self):
        for rec in self:
            rec.alert_date = rec.use_date
