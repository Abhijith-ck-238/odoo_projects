from odoo import models, fields, _
import tempfile
import binascii
import xlrd
import re
from odoo.exceptions import UserError


class GenOffering(models.TransientModel):
    _name = "gen.offering"
    _description = 'Import Offering in xls'

    file = fields.Binary('File')
    import_option = fields.Selection([('xls', 'XLS File')], string='Select',
                                     default='xls')

    def remove(self, string):
        pattern = re.compile(r'\s+')
        return re.sub(pattern, '', string)

    def find_currency(self, currency, exch_rate):
        currency_id = self.env[
            'offering.exchangerate'].search(
            [('currency_name', '=', currency)])
        if currency_id:
            return currency_id
        else:
            currency_id = self.env[
                'offering.exchangerate'].create({
                'currency_name': currency,
                'exchange_rate': exch_rate,
            })
            return currency_id

    def find_access_unit(self, access_unit):
        access_unit_id = self.env['access.units'].search(
            [('name', '=', access_unit)])
        if access_unit_id:
            return access_unit_id
        else:
            access_unit_id = self.env['access.units'].create({
                'name': access_unit})
            return access_unit_id

    def add_configuration(self, config_name, product, iq, currency, row_number):
        fp = tempfile.NamedTemporaryFile(delete=False, suffix=".xlsx")
        fp.write(binascii.a2b_base64(self.file))
        fp.seek(0)
        workbook = xlrd.open_workbook(fp.name)
        subsheets = workbook.sheet_names()
        conflines = []
        bomlines = []

        for sheet in subsheets:
            if sheet == config_name:
                indexx = subsheets.index(sheet)
                config_name = workbook.sheet_by_index(indexx)
                row_headings = config_name.row_values(2)
                if 'Rel.' in row_headings:
                    for r_index in range(5, config_name.nrows):
                        r_val = config_name.row_values(r_index)
                        if all([cell == '' for cell in r_val]):
                            break
                        else:
                            if r_val[3] == '':
                                raise UserError(
                                    _("Error : %s at row %d and coulmn %d") % (
                                        sheet, r_index + 1, 4))
                            if isinstance(r_val[2], float):
                                prdct = self.find_config_product(
                                    r_val[3].strip(), int(float(r_val[2])),
                                    r_val[17].strip())
                            else:
                                prdct = self.find_config_product(
                                    r_val[3].strip(), r_val[2].strip(),
                                    r_val[17].strip())

                            quantity = r_val[4]
                            if quantity == 0 or quantity == '' or not isinstance(
                                    quantity, float):
                                raise UserError(
                                    _("Error : %s at row %d and column %d") % (
                                        sheet, r_index + 1, 5))

                            price_unit = r_val[5]
                            if not isinstance(price_unit,
                                              float) or price_unit == '':
                                raise UserError(
                                    _("Error : %s at row %d and coulmn %d") % (
                                        sheet, r_index + 1, 6))

                            product_id = self.env['product.product'].search([
                                ('name', '=ilike', prdct.name),
                                ('default_code', '=ilike', prdct.default_code)
                            ], limit=1)

                            if not isinstance(quantity, float):
                                raise UserError(
                                    _("Invalid quantity at line %d.") % (
                                                r_index + 1))

                            if product_id:
                                bom_lines = (0, 0, {
                                    'product_id': product_id.id,
                                    'product_qty': quantity,
                                })
                                bomlines.append(bom_lines)
                            else:
                                raise UserError(
                                    _("BoM line creation error at line %d.") % (
                                                r_index + 1))

                            config_lines = (0, 0, {
                                'smn': prdct.default_code,
                                'vendor': self.find_partner(
                                    r_val[16].strip()).id,
                                'product_access_unit': self.find_access_unit(
                                    r_val[17].strip()).id,
                                'product_id': product_id.id,
                                'qty': quantity,
                                'price_unit': price_unit,
                                'policy': r_val[6],
                                'total_price': r_val[8],
                                'so_total_price': r_val[9],
                                'exchange_rate': r_val[7],
                            })
                            conflines.append(config_lines)
                else:
                    for r_index in range(5, config_name.nrows):
                        r_val = config_name.row_values(r_index)
                        if all([cell == '' for cell in r_val]):
                            break
                        else:
                            if r_val[2] == '':
                                raise UserError(
                                    _("Error : %s at row %d and coulmn %d") % (
                                        sheet, r_index + 1, 3))
                            if isinstance(r_val[1], float):
                                prdct = self.find_config_product(
                                    r_val[2].strip(), int(float(r_val[1])),
                                    r_val[17].strip())
                            else:
                                prdct = self.find_config_product(
                                    r_val[2].strip(), r_val[1].strip(),
                                    r_val[17].strip())

                            quantity = r_val[3]
                            if quantity == 0 or quantity == '' or not isinstance(
                                    quantity, float):
                                raise UserError(
                                    _("Error : %s at row %d and coulmn %d") % (
                                        sheet, r_index + 1, 4))

                            price_unit = r_val[4]
                            if not isinstance(price_unit,
                                              float) or price_unit == '':
                                raise UserError(
                                    _("Error : %s at row %d and coulmn %d") % (
                                        sheet, r_index + 1, 5))

                            product_id = self.env['product.product'].search([
                                ('name', '=ilike', prdct.name),
                                ('default_code', '=ilike', prdct.default_code)
                            ], limit=1)

                            if not isinstance(quantity, float):
                                raise UserError(
                                    _("Invalid quantity at line %d.") % (
                                                r_index + 1))

                            if product_id:
                                bom_lines = (0, 0, {
                                    'product_id': product_id.id,
                                    'product_qty': quantity,
                                })
                                bomlines.append(bom_lines)
                            else:
                                raise UserError(
                                    _("BoM line creation error at line %d.") % (
                                                r_index + 1))

                            config_lines = (0, 0, {
                                'smn': prdct.default_code,
                                'vendor': self.find_partner(
                                    r_val[16].strip()).id,
                                'product_access_unit': self.find_access_unit(
                                    r_val[17].strip()).id,
                                'product_id': product_id.id,
                                'qty': quantity,
                                'price_unit': price_unit,
                                'policy': r_val[6],
                                'total_price': r_val[8],
                                'so_total_price': r_val[9],
                                'exchange_rate': r_val[7],
                            })
                            conflines.append(config_lines)

        config_id = self.env['offering.config'].create({
            'iq': iq,
            'product_id': self.env['product.product'].search(
                [('name', '=ilike', product.name)], limit=1).id,
            'product_bom_lines': conflines,
            'currency': currency.id,
        })
        reference = product.name + "-" + iq
        product_tmpl_id = self.env['product.template'].search(
            [('name', '=ilike', product.name)], limit=1)
        if product_tmpl_id:
            # Prevent BoM Cycle
            main_product_variant_ids = product_tmpl_id.product_variant_ids.ids
            for line in bomlines:
                component_product_id = line[2].get('product_id')
                if component_product_id in main_product_variant_ids:
                    raise UserError(
                        _("BoM cycle detected: The product '%s' cannot be used as a component of itself (line %d).") %
                        (product.name, row_number)
                    )

            self.env['mrp.bom'].create({
                'product_tmpl_id': product_tmpl_id.id,
                'bom_line_ids': bomlines,
                'code': reference,
            })
        else:
            raise UserError(
                _("An error occurred during bom creation at line %d.") % row_number)

        return config_id

    def find_partner(self, name):
        partner_id = self.env['res.partner'].search([('name', '=', name)])
        if partner_id:
            return partner_id
        else:
            partner_id = self.env['res.partner'].create({
                'name': name})
            return partner_id

    def find_config_product(self, name, default_code, access_unit):
        if default_code:
            product_id = self.env['product.template'].search(
                [('default_code', '=ilike', default_code)],
                limit=1)
            if product_id:
                return product_id
            else:
                product_access_unit = self.find_access_unit(access_unit)
                product_id = self.env['product.template'].create({
                    'name': name,
                    'default_code': default_code,
                    'type': 'consu',
                    'unit_id': product_access_unit.id})
                return product_id
        else:
            compressed_name = self.remove(name)
            product_id = self.env['product.template'].search(
                [('compressed_name', '=ilike', compressed_name)],
                limit=1)
            if product_id:
                if product_id.default_code:
                    return product_id
                else:
                    default_code = self.env['ir.sequence'].next_by_code(
                        'offering.offering') or 'New'
                    product_id.update({
                        'default_code': default_code,
                    })
                    return product_id
            else:
                default_code = self.env['ir.sequence'].next_by_code(
                    'offering.offering') or 'New'
                product_id = self.env['product.template'].create({
                    'name': name,
                    'default_code': default_code,
                    'type': 'consu'
                })
                return product_id

    def find_subsheet(self, index):
        fp = tempfile.NamedTemporaryFile(delete=False, suffix=".xlsx")
        fp.write(binascii.a2b_base64(self.file))
        fp.seek(0)
        workbook = xlrd.open_workbook(fp.name)
        subsheets = workbook.sheet_names()
        for sheet in subsheets:
            x = re.search('^Specs', sheet)
            if x is not None or sheet.lower() == 'main' or sheet.lower() == 'summary' or sheet.lower() == 'exch':
                pass
            else:
                indexx = subsheets.index(sheet)
                config_name = workbook.sheet_by_index(indexx)
                if indexx == index:
                    return config_name.name

    def import_offering(self):
        if self.import_option == 'xls':
            # try:
            fp = tempfile.NamedTemporaryFile(delete=False, suffix=".xlsx")
            fp.write(binascii.a2b_base64(self.file))
            fp.seek(0)
            workbook = xlrd.open_workbook(fp.name)
            sheet = workbook.sheet_by_index(0)
            if sheet.cell_value(1, 1) != '':
                partner = self.find_partner(sheet.cell_value(1, 1))
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
                                product_name = str(row_val[1] or '').strip() + "*"
                                product = self.find_config_product(product_name,
                                                                   False, False)
                                config_name = self.find_subsheet(index)

                                if isinstance(sheet.cell_value(0, 1), str):
                                    iq = sheet.cell_value(0, 1)
                                    currency = self.find_currency(
                                        row_val[4].strip(),
                                        row_val[6])
                                    config_id = self.add_configuration(
                                        config_name,
                                        product,
                                        iq,
                                        currency, row_number)
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
                                                    [('name', '=ilike',
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
                                product_name = str(row_val[1] or '').strip() + "*"
                                product = self.find_config_product(product_name,
                                                                   False, False)
                                config_name = self.find_subsheet(index)

                                if isinstance(sheet.cell_value(0, 1), str):
                                    iq = sheet.cell_value(0, 1)
                                    currency = self.find_currency(
                                        row_val[4].strip(),
                                        row_val[6])
                                    config_id = self.add_configuration(
                                        config_name,
                                        product,
                                        iq,
                                        currency, row_number)
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
                                                    [('name', '=ilike',
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

                offer_id = self.env['offering.offering'].search(
                    [('iq', '=', sheet.cell_value(0, 1))])
                if offer_id:
                    return {
                        'name': "Warning",
                        'type': 'ir.actions.act_window',
                        'view_type': 'form',
                        'view_mode': 'form',
                        'res_model': 'offering.wizard.warning',
                        'view_id': self.env.ref(
                            'offering_configuration.offer_warning_wizard_view').id,
                        'target': 'new',
                        'context': {'default_offer_id': offer_id.id,
                                    'default_offer_import_id': self.id},
                    }
                else:
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
                            self.env['offering.offering'].create({
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
                        else:
                            col_no = 9
                            row_number = 4
                            raise UserError(
                                _("Error : %s at row %d and coulmn %d") % (
                                    sheet.name, row_number, col_no))
            else:
                col_no = 2
                row_number = 2
                raise UserError(
                    _("Error : %s at row %d and coulmn %d") % (
                        sheet.name, row_number, col_no))
        else:
            raise UserError(
                _("Please insert a valid xls file."))
        return
