from odoo import models, fields, api, _


class LogisticsShipmentinherit(models.Model):
    _inherit = 'logistics.shipment'

    purchase_id = fields.Char(string='Purchase Orders',
                              compute='_get_purchase_orders', store=True)
    contract_id = fields.Char(string='Contracts',
                              compute='_get_contracts', store=True)
    purchase_total = fields.Float(string="PO Total", compute="compute_total_po")
    purchase_total_stored = fields.Float()
    shipment_value = fields.Float(string="Shipment Value")
    fees_percentage = fields.Float(string="Fees Percentage", compute="compute_fees_percentage")
    fees_percentage_stored = fields.Float()
    bill_total = fields.Float(string="Bill Total", compute="compute_bill_total")
    bill_total_stored = fields.Float()
    shipment_type_line_ids = fields.One2many('shipment.type.lines', 'shipment_id', compute="compute_shipment_type_lines")
    bill_count = fields.Integer(compute="compute_bill_count")
    name_seq = fields.Char(string="id", required = True, copy=False, readonly=True, index=True, default="New")


    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name_seq', _('New')) == _('New'):
                vals['name_seq'] = self.env['ir.sequence'].next_by_code(
                    'logistics.shipment.code') or _('New')
                res = super().create(vals_list)
                return res

    def compute_bill_count(self):
        for rcd in self:
            routes = self.env["account.move.line"].search([("shipment_id","=",rcd.id)])
            if routes:
                rcd.bill_count = len(routes)
            else:
                rcd.bill_count = False

    def action_bill_lines(self):
        return{
            'type': 'ir.actions.act_window',
            'name': 'Bill lines',
            'res_model': 'account.move.line',
            'view_mode': 'list',
            'domain': [('shipment_id', '=', self.id)],
        }

    def compute_shipment_type_lines(self):
        for rec in self:
            shipment_types = self.env['shipment.type'].search([])
            shipment_bills = self.env['account.move.line'].search(
                    [('shipment_id', '=', rec.id)])
            if shipment_bills:
                for type in shipment_types:
                    bills = self.env['account.move.line'].search(
                        [('shipment_id', '=', rec.id), ('shipment_type_id', '=', type.id)])
                    if bills:
                        rec.shipment_type_line_ids.create({
                            'shipment_id': rec.id,
                            "shipment_type_id": type.id,
                            "total_value": sum(bills.mapped('price_subtotal')),
                            "per_percentage": sum(bills.mapped('price_subtotal'))/rec.shipment_value if rec.shipment_value else 0,
                            'partner_id': bills[0].move_id.partner_id.id
                        })
            else:
                rec.shipment_type_line_ids =  False

    def compute_bill_total(self):
        for rec in self:
            bills = self.env['account.move.line'].search([('shipment_id', '=', rec.id)])
            if bills:
                rec.bill_total = sum(bills.mapped('price_subtotal'))
                rec.bill_total_stored = sum(bills.mapped('price_subtotal'))
            else:
                rec.bill_total = 0
                rec.bill_total_stored = 0

    def compute_fees_percentage(self):
        for rec in self:
            bills = self.env['account.move.line'].search([('shipment_id', '=', rec.id)])
            if bills and rec.shipment_value:
                rec.fees_percentage = sum(bills.mapped('price_subtotal'))/rec.shipment_value
                rec.fees_percentage_stored = sum(bills.mapped('price_subtotal')) / rec.shipment_value
            else:
                rec.fees_percentage = 0
                rec.fees_percentage_stored = 0

    def compute_total_po(self):
        for rec in self:
            if rec.origin_ids:
                rec.purchase_total = sum(rec.origin_ids.mapped('amount_total'))
                rec.purchase_total_stored =  sum(rec.origin_ids.mapped('amount_total'))
            else:
                rec.purchase_total = 0
                rec.purchase_total_stored = 0

    @api.model
    @api.depends('origin_ids')
    def _get_purchase_orders(self):
        purchase_custom = []
        for rec in self:
            if rec.origin_ids:
                purchase_custom = ','.join([p.name for p in rec.origin_ids])
            else:
                purchase_id = ''
            rec.purchase_id = purchase_custom

    @api.model
    @api.depends('contract_ids')
    def _get_contracts(self):
        contract_custom = []
        for rec in self:
            if rec.contract_ids:
                contract_custom = ','.join([p.name for p in rec.contract_ids])
            else:
                contract_id = ''
            rec.contract_id = contract_custom
