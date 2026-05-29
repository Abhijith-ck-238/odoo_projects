from odoo import models, fields, _
from odoo.exceptions import UserError
from datetime import datetime
import tempfile
import binascii
import xlrd


class GenOfferingWarning(models.TransientModel):
    _name = "offering.wizard.warning"
    _description = 'Display warning'

    offer_id = fields.Many2one('offering.offering', string="offer")
    offer_import_id = fields.Many2one('gen.offering', string="Import offer id")
    msg = fields.Text(
        string="Warning",
        default="The offer with the IQ number is already existing.Do You want to replace it?",
        readonly=True)

    def yes(self):
        fp = tempfile.NamedTemporaryFile(delete=False, suffix=".xlsx")
        fp.write(binascii.a2b_base64(self.offer_import_id.file))
        fp.seek(0)
        workbook = xlrd.open_workbook(fp.name)
        sheet = workbook.sheet_by_index(0)
        partner = self.offer_import_id.find_partner(sheet.cell_value(1, 1))
        lines = []
        index = 2
        item_no = 1
        for row_index in range(8, sheet.nrows):
            row_number = row_index + 1
            row_val = sheet.row_values(row_index)
            if all([cell == '' for cell in row_val]):
                break
            else:
                if row_val[0] == float(item_no):
                    if row_val[1] == '':
                        col_no = 2
                        raise UserError(
                            _("Error : %s at row %d and coulmn %d") % (
                                sheet.name, row_number, col_no))

                    else:
                        product_name = str(row_val[1]).strip() + "*"
                        product = self.offer_import_id.find_config_product(product_name, False, False)
                        config_name = self.offer_import_id.find_subsheet(index)

                        if isinstance(sheet.cell_value(0, 1), str):
                            iq = sheet.cell_value(0, 1)
                            currency = self.offer_import_id.find_currency(
                                row_val[4].strip(),
                                row_val[6])
                            config_id = self.offer_import_id.add_configuration(
                                config_name,
                                product,
                                iq,
                                currency,row_number)
                            qty = row_val[2]
                            if qty == 0 or qty == '' or not isinstance(
                                    qty, float):
                                col_no = 3
                                row_number = row_index + 1
                                raise UserError(
                                    _("Error : %s at row %d and coulmn %d") % (
                                        sheet.name, row_number, col_no))
                            else:
                                unit_price = row_val[7]
                                if isinstance(unit_price,
                                              float) or unit_price == '':
                                    product_lines = (0, 0, {
                                        'product_id': self.env[
                                            'product.product'].search(
                                            [('name', '=',
                                              product.name)],
                                            limit=1).id,
                                        'currency': currency.id,
                                        'qty': row_val[2],
                                        'policy': row_val[3],
                                        'exchange_rate_1': row_val[5],
                                        'exchange_rate': row_val[6],
                                        'unit_price': row_val[7],
                                        'total_price': row_val[8],
                                        'discount': row_val[9],
                                        'price_unit_after_discount':
                                            row_val[
                                                10],
                                        'price_total_after_discount':
                                            row_val[
                                                11],
                                        'offer_unit_price': row_val[12],
                                        'offer_total_price': row_val[
                                            13],
                                        'offer_unit_iqd': row_val[14],
                                        'offer_total_iqd': row_val[15],
                                        'misc': row_val[16],
                                        'final_unit_price_iqd': row_val[
                                            17],
                                        'final_total_price_iqd':
                                            row_val[18],
                                        'final_unit_price_usd': row_val[
                                            19],
                                        'final_total_price_usd':
                                            row_val[20],
                                        'budget_unit_price': row_val[
                                            21],
                                        'budget_total_price': row_val[
                                            22],
                                        'config': config_id.id,
                                    })
                                    lines.append(product_lines)
                                    index = index + 1
                                    item_no = item_no + 1
                                else:
                                    col_no = 8
                                    row_number = row_index + 1
                                    raise UserError(
                                        _("Error : %s at row %d and coulmn %d") % (
                                            sheet.name, row_number,
                                            col_no))
                        else:
                            col_no = 2
                            row_number = 1
                            raise UserError(
                                _("Error : %s at row %d and coulmn %d") % (
                                    sheet.name, row_number, col_no))
                else:
                    if row_val[1] == '':
                        col_no = 2
                        raise UserError(
                            _("Error : %s at row %d and coulmn %d") % (
                                sheet.name, row_number, col_no))

                    else:
                        product_name = str(row_val[1]).strip() + "*"
                        product = self.offer_import_id.find_config_product(product_name, False, False)
                        config_name = self.offer_import_id.find_subsheet(index)

                        if isinstance(sheet.cell_value(0, 1), str):
                            iq = sheet.cell_value(0, 1)
                            currency = self.offer_import_id.find_currency(
                                row_val[4].strip(),
                                row_val[6])
                            config_id = self.offer_import_id.add_configuration(
                                config_name,
                                product,
                                iq,
                                currency,row_number)
                            qty = row_val[2]
                            if qty == 0 or qty == '' or not isinstance(
                                    qty, float):
                                col_no = 3
                                row_number = row_index + 1
                                raise UserError(
                                    _("Error : %s at row %d and coulmn %d") % (
                                        sheet.name, row_number, col_no))
                            else:
                                unit_price = row_val[7]
                                if isinstance(unit_price, float):
                                    product_lines = (0, 0, {
                                        'product_id': self.env[
                                            'product.product'].search(
                                            [('name', '=',
                                              product.name)],
                                            limit=1).id,
                                        'currency': currency.id,
                                        'qty': row_val[2],
                                        'policy': row_val[3],
                                        'exchange_rate_1': row_val[5],
                                        'exchange_rate': row_val[6],
                                        'unit_price': row_val[7],
                                        'total_price': row_val[8],
                                        'discount': row_val[9],
                                        'price_unit_after_discount':
                                            row_val[
                                                10],
                                        'price_total_after_discount':
                                            row_val[
                                                11],
                                        'offer_unit_price': row_val[12],
                                        'offer_total_price': row_val[
                                            13],
                                        'offer_unit_iqd': row_val[14],
                                        'offer_total_iqd': row_val[15],
                                        'misc': row_val[16],
                                        'final_unit_price_iqd': row_val[
                                            17],
                                        'final_total_price_iqd':
                                            row_val[18],
                                        'final_unit_price_usd': row_val[
                                            19],
                                        'final_total_price_usd':
                                            row_val[20],
                                        'budget_unit_price': row_val[
                                            21],
                                        'budget_total_price': row_val[
                                            22],
                                        'config': config_id.id,
                                    })
                                    lines.append(product_lines)
                                    index = index + 1
                                    item_no = item_no + 1
                                else:
                                    col_no = 8
                                    row_number = row_index + 1
                                    raise UserError(
                                        _("Error : %s at row %d and coulmn %d") % (
                                            sheet.name, row_number,
                                            col_no))
                        else:
                            col_no = 2
                            row_number = 1
                            raise UserError(
                                _("Error : %s at row %d and coulmn %d") % (
                                    sheet.name, row_number, col_no))
        xl_date = sheet.cell_value(0, 8)
        if isinstance(xl_date, str) or isinstance(xl_date, int):
            col_no = 9
            row_number = 1
            raise UserError(
                _("Error : %s at row %d and coulmn %d") % (
                    sheet.name, row_number, col_no))
        else:
            datetime_date = xlrd.xldate_as_datetime(int(xl_date), 0)
            date_object = datetime_date.date()
            string_date = date_object.isoformat()
            if isinstance(sheet.cell_value(3, 8), float):
                phone = int(sheet.cell_value(3, 8))
                self.offer_id.write({'product_lines': [(2, rec) for rec in self.offer_id.product_lines.ids]})

                self.offer_id.write({
                    'customer': self.env['res.partner'].search(
                        [('name', '=', partner.name)]).id,
                    'iq': sheet.cell_value(0, 1),
                    'sp_and_labor': sheet.cell_value(0, 5),
                    'labor': sheet.cell_value(1, 5),
                    'site_prep': sheet.cell_value(2, 5),
                    'training': sheet.cell_value(3, 5),
                    'additional': sheet.cell_value(4, 5),
                    'employee_id': sheet.cell_value(1, 8).strip(),
                    'email': sheet.cell_value(2, 8).strip(),
                    'phone': phone,
                    'date': string_date,
                    'payment_method': sheet.cell_value(0, 13),
                    'incoterms': sheet.cell_value(2, 13),
                    'product_lines': lines,
                })
                if self.offer_id.related_sale_order:
                    if self.offer_id.related_sale_order.invoice_ids:
                        for invoice in self.offer_id.related_sale_order.invoice_ids:
                            if invoice.state == 'posted':
                                raise UserError(
                                    _("You have an active invoice for the sale order %s") % (
                                        self.offer_id.related_sale_order.name))
                            else:
                                continue
                        self.offer_id.related_sale_order.write({'order_line': [(2, rec) for rec in
                                                                               self.offer_id.related_sale_order.order_line.ids]})

                        # for rec in self.offer_id.related_sale_order.order_line:
                        #     rec.active = False
                        #     # rec.product_id =False
                            # rec.config =False
                            # rec.price_unit = 0.0
                            # rec.product_uom_qty=0.0
                            # rec.currency_id = False
                            # rec.discount =0.0

                            # {
                            #     "product_id": item.product_id.id,
                            #     "config": item.config.id,
                            #     "price_unit": item.final_unit_price_usd if self.offer_id.offer_currency.name == "USD" or self.offer_id.offer_currency.name == "EUR" else item.final_unit_price_iqd,
                            #     "product_uom_qty": item.qty,
                            #     "currency_id": self.offer_id.offer_currency.id,
                            #     "discount": discount,
                            # }
                            # # rec.unlink()
                        sale_order_vals = {
                            "partner_id": self.offer_id.customer.id,
                            "related_offering_record": self.offer_id.id,
                            "state": "draft",
                            "pricelist_id": self.offer_id.price_list.id,
                            "project_num": self.offer_id.iq
                        }
                        list_of_line_contents = []
                        for item in self.offer_id.product_lines:
                            if item.discount:
                                discount = item.discount * 100
                                list_of_line_contents.append((4, 0, {
                                    "product_id": item.product_id.id,
                                    "config": item.config.id,
                                    "price_unit": item.final_unit_price_usd if self.offer_id.offer_currency.name == "USD" or self.offer_id.offer_currency.name == "EUR" else item.final_unit_price_iqd,
                                    "product_uom_qty": item.qty,
                                    "currency_id": self.offer_id.offer_currency.id,
                                    "discount": discount,
                                }))
                            else:
                                list_of_line_contents.append((4, 0, {
                                    "product_id": item.product_id.id,
                                    "config": item.config.id,
                                    "price_unit": item.final_unit_price_usd if self.offer_id.offer_currency.name == "USD" or self.offer_id.offer_currency.name == "EUR" else item.final_unit_price_iqd,
                                    "product_uom_qty": item.qty,
                                    "currency_id": self.offer_id.offer_currency.id,
                                }))
                        sale_order_vals["order_line"] = list_of_line_contents
                        self.offer_id.related_sale_order.write(sale_order_vals)
                    else:
                        self.offer_id.related_sale_order.write({'order_line': [(2, rec) for rec in
                                                                               self.offer_id.related_sale_order.order_line.ids]})

                        # for rec in self.offer_id.related_sale_order.order_line:
                        #     rec.active = False

                        sale_order_vals = {
                            "partner_id": self.offer_id.customer.id,
                            "related_offering_record": self.offer_id.id,
                            "state": "draft",
                            "pricelist_id": self.offer_id.price_list.id,
                            "project_num": self.offer_id.iq
                        }
                        list_of_line_contents = []
                        for item in self.offer_id.product_lines:
                            if item.discount:
                                discount = item.discount * 100
                                list_of_line_contents.append((0, 0, {
                                    "product_id": item.product_id.id,
                                    "config": item.config.id,
                                    "price_unit": item.final_unit_price_usd if self.offer_id.offer_currency.name == "USD" or self.offer_id.offer_currency.name == "EUR" else item.final_unit_price_iqd,
                                    "product_uom_qty": item.qty,
                                    "currency_id": self.offer_id.offer_currency.id,
                                    "discount": discount,
                                }))
                            else:
                                list_of_line_contents.append((0, 0, {
                                    "product_id": item.product_id.id,
                                    "config": item.config.id,
                                    "price_unit": item.final_unit_price_usd if self.offer_id.offer_currency.name == "USD" or self.offer_id.offer_currency.name == "EUR" else item.final_unit_price_iqd,
                                    "product_uom_qty": item.qty,
                                    "currency_id": self.offer_id.offer_currency.id,
                                }))
                        sale_order_vals["order_line"] = list_of_line_contents
                        self.offer_id.related_sale_order.write(sale_order_vals)
                if self.offer_id.purchase_order_ids:
                    for po in self.offer_id.purchase_order_ids:
                        if po.picking_ids and po.state in ['sent', 'to approve', 'done', 'purchase']:
                            raise UserError(
                                _("You have an active Purchase Order %s") % (
                                    po.name))
                        else:
                            for invoice in po.invoice_ids:
                                if invoice.state in ['posted', 'draft']:
                                    raise UserError(
                                        _("You have an active invoice for the Purchase Order %s") % (
                                            po.name))
                                else:
                                    po.write({'order_line': [(2, rec) for rec in
                                                             po.order_line.ids]})
                                    vendors = {}
                                    for offering_line in self.offer_id.product_lines:
                                        # fetching the currency record because the saved one within the
                                        # config is not from res.currency
                                        res_currency_id = self.env['res.currency'].search(
                                            [('name', '=', offering_line.currency.currency_name)])

                                        for config_line in offering_line.config.product_bom_lines:
                                            # if vendor is not in dict
                                            if not vendors.get(config_line.vendor.id):
                                                vendors[config_line.vendor.id] = res_currency_id.id

                                            #  if vendor is in dict but currency is different
                                            elif vendors.get(config_line.vendor.id) and vendors.get(
                                                    config_line.vendor.id) != res_currency_id.id:
                                                raise UserError(
                                                    "Detected two currencies for the same vendor")

                                            #  if vendor is in dict and currency is the same
                                            else:
                                                pass
                                    for vendor_id, currency_id in vendors.items():

                                        purchase_order_vals = {
                                            "partner_id": vendor_id,
                                            "origin": self.offer_id.name,
                                            "currency_id": currency_id,
                                            "related_offering_record": self.offer_id.id,
                                            "date_planned": datetime.today()
                                        }

                                        list_of_line_contents = []
                                        for line in self.offer_id.product_lines:
                                            qtyy = line.qty
                                            for configline in line.config.product_bom_lines:
                                                if configline.vendor.id == vendor_id:
                                                    list_of_line_contents.append((0, 0, {
                                                        "product_id": configline.product_id.id,
                                                        "price_unit": configline.total_price,
                                                        "product_qty": configline.qty * qtyy,
                                                        "name": configline.product_id.name,
                                                        "product_uom": configline.product_id.uom_id.id}))
                                        purchase_order_vals["order_line"] = list_of_line_contents
                                        po.write(purchase_order_vals)

                if self.offer_id.related_contract:
                    self.offer_id.related_contract.write({'product_lines': [(2, rec) for rec in
                                                                            self.offer_id.related_contract.product_lines.ids]})
                    list_of_line_contents = []
                    for item in self.offer_id.product_lines:
                        if item.qty == 1:
                            list_of_line_contents.append(
                                (0, 0, {
                                    "product_id": item.product_id.id,
                                    "product_char": item.product_id.name,
                                    "price": item.offer_unit_price,
                                    "qty": item.qty,
                                    "config": item.config.id}))
                        else:
                            for i in range(0, item.qty):
                                list_of_line_contents.append(
                                    (0, 0, {
                                        "product_id": item.product_id.id,
                                        "product_char": item.product_id.name,
                                        "price": item.offer_unit_price,
                                        "qty": 1,
                                        "config": item.config.id
                                    }))

                    contract_vals = {
                        "partner_id": self.offer_id.customer.id,
                        "related_offering_record": self.offer_id.id,
                        "iq": self.offer_id.iq,
                        "number": self.offer_id.contract_no,
                        "signed_date": self.offer_id.sign_date,
                        "contract_categ": self.offer_id.contract_type,
                        "contract_signed_by": self.offer_id.signed_by.id,
                        "product_lines": list_of_line_contents,
                    }

                    self.offer_id.related_contract.write(contract_vals)

            else:
                col_no = 9
                row_number = 4
                raise UserError(
                    _("Error : %s at row %d and coulmn %d") % (
                        sheet.name, row_number, col_no))
        return

    def no(self):
        return
