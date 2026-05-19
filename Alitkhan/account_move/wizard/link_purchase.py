from odoo import models, fields, _
from odoo.exceptions import UserError


class LinkPurchase(models.TransientModel):
    _name = "link.purchase"
    _description = 'Link Bill to Purchase order'

    bill_id = fields.Many2one('account.move', string="Bill")
    purchase_id = fields.Many2one("purchase.order", string="Purchase Order",
                                  domain="[('state', '=', 'purchase')]")

    def link_purchase_order(self):
        invoice_lines = []
        for line in self.purchase_id.order_line:
            invoice_lines.append(line.product_id.id)
        if self.purchase_id.partner_id == self.bill_id.partner_id:
            for inv_line in self.bill_id.invoice_line_ids:
                if inv_line.product_id.id in invoice_lines:
                    res = self.env['purchase.order.line'].search([
                        ('product_id', '=', inv_line.product_id.id),
                        ('order_id', '=', self.purchase_id.id)])
                    total_qty = 0
                    total_invoiced_qty = 0
                    for line1 in res:
                        total_qty = total_qty + line1.product_qty
                        total_invoiced_qty = total_invoiced_qty + line1.qty_invoiced
                    total_qty_to_invoice = total_qty - total_invoiced_qty
                    invoice_line_qty = inv_line.quantity

                    if invoice_line_qty <= total_qty_to_invoice:
                        for i in range(0, len(res)):
                            if res[i].product_qty == res[i].qty_invoiced:
                                continue
                            else:
                                unit_price = res[i].price_unit
                                qty_need = res[i].product_qty - res[
                                    i].qty_invoiced
                                if unit_price == inv_line.price_unit:
                                    if qty_need <= invoice_line_qty:
                                        res[i].qty_invoiced = res[
                                                                  i].qty_invoiced + qty_need
                                        invoice_line_qty = invoice_line_qty - qty_need
                                        if invoice_line_qty > 0:
                                            continue
                                        else:
                                            inv_line.purchase_line_id = res[
                                                i].id
                                            self.bill_id.purchase_id = self.purchase_id.id
                                            self.purchase_id.invoice_ids = [
                                                (4, self.bill_id.id, None)]
                                            self.purchase_id.invoice_count = len(
                                                self.purchase_id.invoice_ids)
                                            break

                                    else:

                                        res[i].qty_invoiced = res[
                                                                  i].qty_invoiced + invoice_line_qty

                                        inv_line.purchase_line_id = res[
                                            i].id
                                        self.bill_id.purchase_id = self.purchase_id.id
                                        self.purchase_id.invoice_ids = [
                                            (4, self.bill_id.id, None)]
                                        self.purchase_id.invoice_count = len(
                                            self.purchase_id.invoice_ids)
                                        break
                                else:
                                    return {
                                        'name': "Warning",
                                        'type': 'ir.actions.act_window',
                                        'view_type': 'form',
                                        'view_mode': 'form',
                                        'res_model': 'wizard.warning',
                                        'view_id': self.env.ref(
                                            'account_move'
                                            '.warning_wizard_view').id,
                                        'target': 'new',
                                        'context': {
                                            'default_purchase_link_id': self.id},
                                    }
                    else:
                        raise UserError(
                            _("The product '%s' total quantity is not "
                              "matching with Purchase Order "
                              "Line.") % inv_line.product_id.name)
                else:
                    raise UserError(
                        _("The product '%s' is not found on purchase "
                          "order.") % inv_line.product_id.name)
        else:
            raise UserError(
                _("The vendor '%s' is mismatching with Purchase"
                  " Order's Vendor.") % self.bill_id.partner_id.name)
        return

    def vendor_bill(self):
        invoice_lines = []
        for line in self.purchase_id.order_line:
            invoice_lines.append(line.product_id.id)
        for inv_line in self.bill_id.invoice_line_ids:
            if inv_line.product_id.id in invoice_lines:
                res = self.env['purchase.order.line'].search([
                    ('product_id', '=', inv_line.product_id.id),
                    ('order_id', '=', self.purchase_id.id)])
                total_qty = 0
                total_invoiced_qty = 0
                for line1 in res:
                    total_qty = total_qty + line1.product_qty
                    total_invoiced_qty = total_invoiced_qty + line1.qty_invoiced
                total_qty_to_invoice = total_qty - total_invoiced_qty
                invoice_line_qty = inv_line.quantity
                if invoice_line_qty <= total_qty_to_invoice:
                    for i in range(0, len(res)):
                        if res[i].product_qty == res[i].qty_invoiced:
                            continue
                        else:
                            unit_price = res[i].price_unit
                            qty_need = res[i].product_qty - res[
                                i].qty_invoiced
                            # if unit_price == inv_line.price_unit:
                            if qty_need <= invoice_line_qty:

                                res[i].qty_invoiced = res[
                                                          i].qty_invoiced + qty_need

                                invoice_line_qty = invoice_line_qty - qty_need

                                if invoice_line_qty > 0:
                                    continue
                                else:
                                    inv_line.purchase_line_id = res[
                                        i].id
                                    self.bill_id.purchase_id = self.purchase_id.id
                                    self.purchase_id.invoice_ids = [
                                        (4, self.bill_id.id, None)]
                                    self.purchase_id.invoice_count = len(
                                        self.purchase_id.invoice_ids)
                                    break
                            else:
                                res[i].qty_invoiced = res[
                                                          i].qty_invoiced + invoice_line_qty

                                inv_line.purchase_line_id = res[
                                    i].id
                                self.bill_id.purchase_id = self.purchase_id.id
                                self.purchase_id.invoice_ids = [
                                    (4, self.bill_id.id, None)]
                                self.purchase_id.invoice_count = len(
                                    self.purchase_id.invoice_ids)
                                break
                else:
                    raise UserError(
                        _("The product '%s' total quantity is not "
                          "matching with Purchase Order "
                          "Line.") % inv_line.product_id.name)
            else:
                raise UserError(
                    _("The product '%s' is not found on purchase "
                      "order.") % inv_line.product_id.name)

        return
