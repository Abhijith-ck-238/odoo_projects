from odoo import fields, models


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    is_rfid_difference_exist = fields.Boolean(string="RFID Difference")
    rfid_extra_quantity_ids = fields.One2many('extra.rfid.quantity', 'picking_id', string='Extra RFID Quantity')

    def action_open_fetch_wizard(self):
        return {
            'name': "Confirmation",
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'fetch.confirm.wizard',
            'view_id': self.env.ref(
                'rfid_connector.fetch_confirm_wizard_view').id,
            'target': 'new',
        }

    def action_fetch_rfid_data(self):
        last_transfer = self.env['rfid.transfer'].search([('picking_id', '=', self.id)], limit=1,order='id desc')
        product_ids = []
        for rec in self.move_ids_without_package:
            print(last_transfer.read(),'abdd main transfer refff',rec.read())
            transfer_line = self.env['rfid.transfer.line'].search(
                [('rfid_transfer_id', '=', last_transfer.id), ('product_ref', '=', rec.product_id.default_code)])
            if rec.product_id.tracking != 'none':
                if rec.product_id in product_ids:
                    move_lines = self.move_ids_without_package.search([('product_id', '=', rec.product_id.id),('picking_id', '=', self.id), ('id', '!=', rec.id)])
                    quantity_left = sum(transfer_line.mapped('product_qty'))-sum(move_lines.mapped('rfid_qty'))
                    if quantity_left > rec.product_uom_qty:
                        rec.rfid_qty = rec.product_uom_qty
                    else:
                        rec.rfid_qty = quantity_left
                    transfer_line_ids = self.env['rfid.transfer.line'].search([('rfid_transfer_id', '=', last_transfer.id), ('is_completed', '=', False),
                                                                               ('product_ref', '=', rec.product_id.default_code)], limit=int(rec.product_uom_qty))
                    for transfer_line_id in transfer_line_ids:
                        if transfer_line_id.product_ref == rec.product_id.default_code:
                            if transfer_line_id.lot_id:
                                move_line_id = self.env['stock.move.line'].search([('product_id', '=', rec.product_id.id),
                                                                                   ('move_id', '=', rec.id),('lot_id', '=',transfer_line_id.lot_id.id)])
                                total_quantity = sum(self.env['stock.move.line'].search([('move_id', '=', rec.id)]).mapped('product_uom_qty'))
                                if move_line_id:
                                    if total_quantity < move_line_id.move_id.product_uom_qty:
                                        move_line_id.write({
                                            'product_uom_qty': move_line_id.product_uom_qty + transfer_line_id.product_qty,
                                        })
                                        transfer_line_id.is_completed = True
                                else:
                                    if total_quantity < rec.product_uom_qty:
                                        self.env['stock.move.line'].create({
                                            'product_id': rec.product_id.id,
                                            'location_id': self.location_id.id,
                                            'product_uom_qty': transfer_line_id.product_qty,
                                            'product_uom_id': rec.product_uom.id,
                                            'move_id': rec.id,
                                            'lot_id':transfer_line_id.lot_id.id,
                                            'location_dest_id': self.location_dest_id.id,
                                            'picking_id': self.id
                                        })
                                    transfer_line_id.is_completed = True
                        transfer_line_id.is_completed = True
                else:
                    if sum(transfer_line.mapped('product_qty')) > rec.product_uom_qty:
                        rec.rfid_qty = rec.product_uom_qty
                    else:
                        rec.rfid_qty = sum(transfer_line.mapped('product_qty'))
                    transfer_line_ids = self.env['rfid.transfer.line'].search([('rfid_transfer_id', '=', last_transfer.id),('is_completed', '=', False),
                                                                               ('product_ref', '=', rec.product_id.default_code)],limit=int(rec.product_uom_qty))
                    for transfer_line_id in transfer_line_ids:
                        if transfer_line_id.product_ref == rec.product_id.default_code:
                            if transfer_line_id.lot_id:
                                move_line_id = self.env['stock.move.line'].search( [('product_id', '=', rec.product_id.id),('move_id', '=', rec.id),
                                                                                    ('lot_id', '=', transfer_line_id.lot_id.id)])
                                total_quantity = sum(self.env['stock.move.line'].search([('move_id', '=', rec.id)]).mapped('product_uom_qty'))
                                if move_line_id:
                                    if total_quantity < move_line_id.move_id.product_uom_qty:
                                        move_line_id.write({
                                            'product_uom_qty': move_line_id.product_uom_qty + transfer_line_id.product_qty,
                                        })
                                        transfer_line_id.is_completed = True
                                else:
                                    if total_quantity < rec.product_uom_qty:
                                        self.env['stock.move.line'].create({
                                            'product_id': rec.product_id.id,
                                            'location_id': self.location_id.id,
                                            'product_uom_qty': transfer_line_id.product_qty,
                                            'product_uom_id': rec.product_uom.id,
                                            'move_id': rec.id,
                                            'lot_id': transfer_line_id.lot_id.id,
                                            'location_dest_id': self.location_dest_id.id,
                                            'picking_id': self.id
                                        })
                                    transfer_line_id.is_completed = True
                        transfer_line_id.is_completed = True
                    product_ids.append(rec.product_id)
            else:
                print('abddd elseee')
                if rec.product_id in product_ids:
                    print(rec.product_id,'abddd prodct idd',product_ids)
                    move_lines = self.move_ids_without_package.search([('product_id', '=', rec.product_id.id),('picking_id', '=', self.id),('id','!=', rec.id)])
                    quantity_left = sum(transfer_line.mapped('product_qty'))-sum(move_lines.mapped('rfid_qty'))
                    if quantity_left > rec.product_uom_qty:
                        rec.rfid_qty = rec.product_uom_qty
                    else:
                        rec.rfid_qty = quantity_left
                    transfer_line_ids = self.env['rfid.transfer.line'].search(
                        [('rfid_transfer_id', '=', last_transfer.id),
                         ('is_completed', '=', False),
                         ('product_ref', '=', rec.product_id.default_code)],
                        limit=int(rec.product_uom_qty))
                    for transfer_line_id in transfer_line_ids:
                        if transfer_line_id.product_ref == rec.product_id.default_code:
                            move_line_id = self.env[
                                'stock.move.line'].search(
                                [('product_id', '=', rec.product_id.id),
                                 ('move_id', '=', rec.id)])
                            total_quantity = sum(
                                self.env['stock.move.line'].search(
                                    [('move_id', '=', rec.id)]).mapped(
                                    'product_uom_qty'))
                            if move_line_id:
                                if total_quantity < move_line_id.move_id.product_uom_qty:
                                    move_line_id.write({
                                        'product_uom_qty': move_line_id.product_uom_qty + transfer_line_id.product_qty,
                                    })
                                    transfer_line_id.is_completed = True
                            else:
                                if total_quantity < rec.product_uom_qty:
                                    self.env['stock.move.line'].create({
                                        'product_id': rec.product_id.id,
                                        'location_id': self.location_id.id,
                                        'product_uom_qty': transfer_line_id.product_qty,
                                        'product_uom_id': rec.product_uom.id,
                                        'move_id': rec.id,
                                        'location_dest_id': self.location_dest_id.id,
                                        'picking_id': self.id
                                    })
                                transfer_line_id.is_completed = True
                        transfer_line_id.is_completed = True
                else:
                    print(transfer_line.read(),'abddd prdct ',rec.product_uom_qty)
                    if sum(transfer_line.mapped('product_qty')) > rec.product_uom_qty:
                        rec.rfid_qty = rec.product_uom_qty
                    else:
                        rec.rfid_qty = sum(transfer_line.mapped('product_qty'))
                    transfer_line_ids = self.env['rfid.transfer.line'].search(
                        [('rfid_transfer_id', '=', last_transfer.id),
                         ('is_completed', '=', False),
                         ('product_ref', '=', rec.product_id.default_code)],
                        limit=int(rec.product_uom_qty))
                    for transfer_line_id in transfer_line_ids:
                        if transfer_line_id.product_ref == rec.product_id.default_code:
                            move_line_id = self.env[
                                'stock.move.line'].search(
                                [('product_id', '=', rec.product_id.id),
                                 ('move_id', '=', rec.id),])
                            total_quantity = sum(
                                self.env['stock.move.line'].search(
                                    [('move_id', '=', rec.id)]).mapped(
                                    'product_uom_qty'))
                            if move_line_id:
                                if total_quantity < move_line_id.move_id.product_uom_qty:
                                    move_line_id.write({
                                        'product_uom_qty': move_line_id.product_uom_qty + transfer_line_id.product_qty,
                                    })
                                    transfer_line_id.is_completed = True
                            else:
                                if total_quantity < rec.product_uom_qty:
                                    self.env['stock.move.line'].create({
                                        'product_id': rec.product_id.id,
                                        'location_id': self.location_id.id,
                                        'product_uom_qty': transfer_line_id.product_qty,
                                        'product_uom_id': rec.product_uom.id,
                                        'move_id': rec.id,
                                        'location_dest_id': self.location_dest_id.id,
                                        'picking_id': self.id
                                    })
                                transfer_line_id.is_completed = True
                        transfer_line_id.is_completed = True
                    product_ids.append(rec.product_id)
        self.rfid_extra_quantity_ids.unlink()
        extra_transfer_lines = self.env['rfid.transfer.line'].search([('rfid_transfer_id', '=', last_transfer.id),('is_completed', '=',False)])
        for extra_transfer_line in extra_transfer_lines:
            product = self.env['product.product'].search([('default_code', '=', extra_transfer_line.product_ref)],limit=1)
            if extra_transfer_line.lot_id:
                extra_quantity_line = self.env['extra.rfid.quantity'].search(
                    [('product_id', '=', product.id),
                     ('picking_id', '=', self.id),('lot_id', '=', extra_transfer_line.lot_id.id)])
                if extra_quantity_line:
                    extra_quantity_line.write({
                        'quantity': extra_quantity_line.quantity + extra_transfer_line.product_qty,
                    })
                else:
                    self.env['extra.rfid.quantity'].create({
                        'product_id': product.id,
                        'quantity': extra_transfer_line.product_qty,
                        'picking_id': self.id,
                        'lot_id':  extra_transfer_line.lot_id.id,
                    })
                extra_transfer_line.is_completed = True
            else:
                extra_quantity_line = self.env['extra.rfid.quantity'].search([('product_id', '=', product.id), ('picking_id', '=', self.id)])
                if extra_quantity_line:
                    extra_quantity_line.write({
                        'quantity': extra_quantity_line.quantity + extra_transfer_line.product_qty,
                    })
                else:
                    self.env['extra.rfid.quantity'].create({
                        'product_id': product.id,
                        'quantity': extra_transfer_line.product_qty,
                        'picking_id': self.id
                    })
                extra_transfer_line.is_completed = True
        if self.rfid_extra_quantity_ids:
            self.is_rfid_difference_exist = True
        else:
            self.is_rfid_difference_exist = False
        for line in self.move_ids_without_package:
            if line.rfid_qty < line.product_uom_qty:
                self.is_rfid_difference_exist = True
        if self.is_rfid_difference_exist:
            self.message_post(body="There is some difference between RFID transfer and this transfer.")

    def action_open_done_wizard(self):
        return {
            'name': "Confirmation",
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'done.confirm.wizard',
            'view_id': self.env.ref(
                'rfid_connector.done_confirm_wizard_view').id,
            'target': 'new',
        }

    def action_rfid_done(self):
        print(self.move_line_ids_without_package,'abd move_line_ids_without_package')
        for rec in self.move_line_ids_without_package:
            if rec.quantity:
                rec.qty_done = rec.quantity

    def action_open_scan_wizard(self):
        return {
            'name': "Confirmation",
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'scan.confirm.wizard',
            'view_id': self.env.ref('rfid_connector.scan_confirm_wizard_view').id,
            'target': 'new',
        }

    def action_scan_product(self):
        out_transfers = self.env['rfid.out.transfer'].search([])
        if out_transfers:
            out_transfers.unlink()

        self.env['rfid.out.transfer'].create(
            {
                'picking_id': self.id
            }
        )