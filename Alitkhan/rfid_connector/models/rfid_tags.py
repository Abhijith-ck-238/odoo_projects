from odoo import models, fields, api


class RfidTags(models.Model):
    _name = 'rfid.tag.epc'
    _description = 'RFID Tag EPC'
    _rec_name = 'epc_id'

    sequence = fields.Char("Sequence",readonly=True, copy=False)
    epc_id = fields.Char("EPC Id")
    product_id = fields.Many2one('product.template', string="Product")
    lot_id = fields.Many2one('stock.lot', string='Lot/Serial')
    lot = fields.Char(String="Lot/Serial", related='lot_id.name')
    reference = fields.Char(string="Reference", related="product_id.default_code")
    picking_id = fields.Many2one('stock.picking', string="Transfer")

    def create_rfid_tag(self,product_id):
        epc = self.create({
            'product_id': int(product_id),
        })
        return epc.sequence

    def create_picking_rfid_tag(self, line_ids):
        zpl = []
        for line in line_ids:
            move_line = self.env['stock.move'].browse(line)
            for i in range(int(move_line.product_uom_qty)):
                if move_line.lot_id.id:
                    epc = self.create({
                        'product_id': move_line.product_id.product_tmpl_id.id,
                        'picking_id': move_line.picking_id.id,
                        'lot_id': move_line.lot_id.id
                    })
                    zpl += ["^XA^RFW,A^FD" + epc.sequence + "^FS^FO30,50^A0N,44,33^FD" +
                        move_line.product_id.display_name + "^FS^FO100,100^A0N,44,33^FD" +
                        (move_line.product_id.default_code if move_line.product_id.default_code else "") + "^FS^FO100,150^A0N,44,33^FD" +
                        move_line.lot_id.name + "^FS"]
                    if move_line.product_id.barcode:
                        zpl += ["^FO100,200^BY3^BCN,100,Y,N,N^FD" + move_line.product_id.barcode + "^FS"]
                    zpl += ["^XZ"]
                else:
                    epc = self.create({
                        'product_id': move_line.product_id.product_tmpl_id.id,
                        'picking_id': move_line.picking_id.id,
                    })
                    zpl += [
                        "^XA^RFW,A^FD" + epc.sequence + "^FS^FO30,50^A0N,44,33^FD" +
                        move_line.product_id.display_name + "^FS^FO100,100^A0N,44,33^FD" +
                        (move_line.product_id.default_code if move_line.product_id.default_code else "") + "^FS"]
                    if move_line.product_id.barcode:
                        zpl += [
                            "^FO100,200^BY3^BCN,100,Y,N,N^FD" + move_line.product_id.barcode + "^FS"]
                    zpl += ["^XZ"]
        zpl = (''.join(zpl))
        return zpl

    def create_lot_rfid_tag(self, product_id,lot_id):
        product = self.env["product.product"].browse(int(product_id))
        epc = self.create({
            'product_id': int(product.product_tmpl_id.id),
            'lot_id': int(lot_id)
        })

        res = {
            'sequence': epc.sequence,
            'default_code': product.default_code,
            'barcode': product.barcode,
            'product_name':product.name
        }
        return res


    @api.model
    def create(self, vals):
        if vals.get('sequence', 'New') == 'New':
            vals['sequence'] = self.env['ir.sequence'].next_by_code(
                'epc.seq') or 'New'
            vals['epc_id'] = vals['sequence'].encode("utf-8").hex().upper()
            return super(RfidTags, self).create(vals)
