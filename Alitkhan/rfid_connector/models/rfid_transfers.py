from odoo import fields, models, api


class RfidTransfers(models.Model):
    _name = "rfid.transfer"
    _description = "RFID Transfer"
    _rec_name = 'transfer'

    transfer = fields.Char("Transfer")
    transfer_type = fields.Char("Transfer Type")
    date = fields.Date("Date")
    picking_id = fields.Many2one('stock.picking',string='Transfer Ref')
    transfer_line_ids = fields.One2many('rfid.transfer.line', 'rfid_transfer_id', string="Transfer Lines")
    total_quantity = fields.Float(string="Total Quantity", compute='compute_total_quantity', store=True)

    @api.depends('transfer_line_ids')
    def compute_total_quantity(self):
        for rec in self:
            rec.total_quantity = sum(rec.transfer_line_ids.mapped('product_qty'))


class RfidTransferLine(models.Model):
    _name = 'rfid.transfer.line'
    _description = "RFID Transfer Line"

    rfid_transfer_id = fields.Many2one('rfid.transfer', string='RFID Transfer')
    epc_id = fields.Char("Product Epc")
    product_name = fields.Char("Product Name")
    product_ref = fields.Char("Internal Reference")
    product_qty = fields.Float("Product Quantity")
    lot_number = fields.Char("Lot/Serial", compute="compute_lot_number")
    lot_id = fields.Many2one('stock.lot', compute='compute_lot_id', store=True)
    is_completed = fields.Boolean()
    is_extra = fields.Boolean()
    is_available = fields.Boolean("Transfer Exist")

    # @api.depends('epc_id')
    # def compute_lot_number(self):
    #     for rec in self:
    #         rfid_tag = self.env['rfid.tag.epc'].search(
    #             [('epc_id', '=', rec.epc_id)])
    #         if rfid_tag.lot:
    #             rec.lot_number = rfid_tag.lot
    #             rec.lot_id = rfid_tag.lot_id.id
    #         else:
    #             rec.lot_number = False
    #             rec.lot_id = False
    @api.depends('epc_id')
    def compute_lot_number(self):
        """Compute lot_number (non-stored field)"""
        for rec in self:
            rfid_tag = self.env['rfid.tag.epc'].search(
                [('epc_id', '=', rec.epc_id)], limit=1)
            rec.lot_number = rfid_tag.lot if rfid_tag.lot else False

    @api.depends('epc_id')
    def compute_lot_id(self):
        """Compute lot_id (stored field)"""
        for rec in self:
            rfid_tag = self.env['rfid.tag.epc'].search(
                [('epc_id', '=', rec.epc_id)], limit=1)
            rec.lot_id = rfid_tag.lot_id.id if rfid_tag.lot_id else False
