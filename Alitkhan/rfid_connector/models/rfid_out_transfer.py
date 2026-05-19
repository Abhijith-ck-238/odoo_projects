from odoo import fields, models

class RfidOutTransfer(models.TransientModel):
    _name ='rfid.out.transfer'
    _description = 'Rfid Out Transfer'

    picking_id = fields.Many2one('stock.picking', string="Out Transfer")


