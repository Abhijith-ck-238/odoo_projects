import logging
import tempfile
import binascii
import xlrd
import io
from datetime import datetime
from odoo.exceptions import UserError
from odoo import models, fields, exceptions, _
import openpyxl

_logger = logging.getLogger(__name__)

try:
    import csv

except ImportError:
    _logger.debug('Cannot `import csv`.')
try:
    import xlwt
except ImportError:
    _logger.debug('Cannot `import xlwt`.')
try:
    import cStringIO
except ImportError:
    _logger.debug('Cannot `import cStringIO`.')
try:
    import base64
except ImportError:
    _logger.debug('Cannot `import base64`.')


class CustomGenSale(models.TransientModel):
    _inherit = "gen.sale"

    def _my_new_selection(self):
        lst = [('csv', 'CSV File'), ('xls', 'XLS File')]
        try:
            lst.remove([item for item in lst if item[0] == 'csv'][0])
        except IndexError as e:
            pass
        return lst

    def _my_new_selection_import_product(self):
        lst = [('name', 'Name'), ('code', 'Code'), ('barcode', 'Barcode')]
        try:
            lst.remove([item for item in lst if item[0] == 'name'][0])
        except IndexError as e:
            pass
        return lst

    import_option = fields.Selection(selection='_my_new_selection', string='Select', default='xls')
    import_prod_option = fields.Selection(selection='_my_new_selection_import_product',
                                          string='Import Product By ', default='code')

    def make_order_line(self, values, sale_id):
        product_obj = self.env['product.product']
        order_line_obj = self.env['sale.order.line']
        current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        if self.import_prod_option == 'barcode':
            product_search = product_obj.search([('barcode', '=', values['product'])])
        elif self.import_prod_option == 'code':
            product_search = product_obj.search([('default_code', '=', values['product'])], limit=1)
        else:
            product_search = product_obj.search([('name', '=', values['product'])])

        product_uom = self.env['uom.uom'].search([('name', '=', values.get('uom'))])
        unit_id = self.env['access.units'].search([('name', '=', values.get('access_unit'))])
        product_category = self.env['product.category'].search([('name', '=', values.get('product_category'))])
        vendor = self.env['res.partner'].search(
            [('name', '=', values.get('vendor'))])

        if product_uom.id == False:
            raise UserError(_(' "%s" Product UOM category is not available.') % values.get('uom'))

        if not unit_id:
            unit_id = self.env['access.units'].create({
                'name': values.get('access_unit'),
            })

        if not product_category:
            product_category = self.env['product.category'].create({
                'name': values.get('product_category'),
            })
        if not vendor:
            vendor = self.env['res.partner'].create({
                'name': values.get('vendor'),
            })

        if product_search:
            product_id = product_search[0]
        else:
            if self.import_prod_option == 'code':
                product_id = product_obj.create({
                    'name': values.get('description'),
                    'default_code': values.get('product'),
                    'lst_price': float(values.get('price')),
                    'uom_id': product_uom.id,
                    'uom_po_id': product_uom.id,
                    'unit_id': unit_id.id,
                    'categ_id': product_category.id,
                    'type': 'consu',
                })
            else:
                raise UserError(
                    _('%s product is not found" .\n If you want to create product then first select Import Product By Name option .') % values.get(
                        'product'))

        tax_ids = []
        if values.get('tax'):
            if ';' in values.get('tax'):
                tax_names = values.get('tax').split(';')
                for name in tax_names:
                    tax = self.env['account.tax'].search([('name', '=', name), ('type_tax_use', '=', 'sale')])
                    if not tax:
                        raise UserError(_('"%s" Tax not in your system') % name)
                    tax_ids.append(tax.id)

            elif ',' in values.get('tax'):
                tax_names = values.get('tax').split(',')
                for name in tax_names:
                    tax = self.env['account.tax'].search([('name', '=', name), ('type_tax_use', '=', 'sale')])
                    if not tax:
                        raise UserError(_('"%s" Tax not in your system') % name)
                    tax_ids.append(tax.id)
            else:
                tax_names = values.get('tax').split(',')
                for name in tax_names:
                    tax = self.env['account.tax'].search([('name', '=', name), ('type_tax_use', '=', 'sale')])
                    if not tax:
                        raise UserError(_('"%s" Tax not in your system') % name)
                    tax_ids.append(tax.id)

        so_order_lines = order_line_obj.create({
            'order_id': sale_id.id,
            'product_id': product_id.id,
            'name': product_id.name,
            'product_uom_qty': values.get('quantity'),
            'product_uom': product_uom.id,
            'price_unit': values.get('price'),
            'discount': values.get('discount'),
            'vendor_id':vendor.id,
            'vendor_price': values.get('vendor_price')

        })
        if tax_ids:
            so_order_lines.write({'tax_id': ([(6, 0, tax_ids)])})
        return True

    def make_sale(self, values):
        sale_obj = self.env['sale.order']
        if self.sequence_opt == "custom":
            if values.get('order') == '':
                raise UserError(_('You must set a Sale order number on the excel sheet or choose the sequence option '
                                  'as \' Use System Default Sequence Number \' to import the sale order.'))

            sale_search = sale_obj.search([
                ('name', '=', values.get('order'))
            ])
        else:
            sale_search = sale_obj.search([
                ('sale_name', '=', values.get('order'))
            ])
        if sale_search:
            sale_search = sale_search[0]
            if sale_search.partner_id.name == values.get('customer'):
                if sale_search.pricelist_id.name == values.get('pricelist'):
                    lines = self.make_order_line(values, sale_search)
                    return sale_search
                else:
                    raise UserError(_('Pricelist is different for "%s" .\n Please define same.') % values.get('order'))
            else:
                raise UserError(_('Customer name is different for "%s" .\n Please define same.') % values.get('order'))

        else:
            if values.get('seq_opt') == 'system':
                name = self.env['ir.sequence'].next_by_code('sale.order')
            elif values.get('seq_opt') == 'custom':
                name = values.get('order')
            partner_id = self.find_partner(values.get('customer'))
            currency_id = self.find_currency(values.get('pricelist'))
            user_id = self.find_user(values.get('user'))
            order_date = self.make_order_date(values.get('date'))
            sale_id = sale_obj.create({
                'partner_id': partner_id.id,
                'pricelist_id': currency_id.id,
                'name': name,
                'user_id': user_id.id,
                'date_order': order_date,
                'custom_seq': True if values.get('seq_opt') == 'custom' else False,
                'system_seq': True if values.get('seq_opt') == 'system' else False,
                'sale_name': values.get('order')

            })
            self.make_order_line(values, sale_id)
            return sale_id

    def import_sale(self):

        """Load Inventory data from the CSV file."""
        if self.import_option == 'csv':
            keys = ['order', 'customer', 'pricelist', 'product', 'quantity', 'uom', 'description', 'price', 'user',
                    'tax', 'date','vendor','vendor_price']
            csv_data = base64.b64decode(self.file)
            data_file = io.StringIO(csv_data.decode("utf-8"))
            data_file.seek(0)
            file_reader = []
            sale_ids = []
            csv_reader = csv.reader(data_file, delimiter=',')
            try:
                file_reader.extend(csv_reader)
            except Exception:
                raise exceptions.UserError(_("Invalid file!"))
            values = {}
            for i in range(len(file_reader)):
                field = list(map(str, file_reader[i]))
                values = dict(zip(keys, field))
                if values:
                    if i == 0:
                        continue
                    else:
                        values.update({'option': self.import_option, 'seq_opt': self.sequence_opt})
                        res = self.make_sale(values)
                        sale_ids.append(res)
            if self.stage == 'confirm':
                for res in sale_ids:
                    if res.state in ['draft', 'sent']:
                        res.action_confirm()

        else:
            if not self.file:
                raise UserError(
                    "No file uploaded. Please upload a valid Excel (.xlsx) file.")

            fp = tempfile.NamedTemporaryFile(delete=False, suffix=".xlsx")
            fp.write(binascii.a2b_base64(self.file))
            fp.seek(0)
            values = {}
            sale_ids = []
            workbook = xlrd.open_workbook(fp.name)
            # workbook = openpyxl.load_workbook(fp.name)
            sheet = workbook.sheet_by_index(0)
            if self.sequence_opt == 'system':
                product_lines = []
                for row_no in range(sheet.nrows):
                    val = {}
                    if row_no <= 0:
                        fields = map(lambda row: row.value.encode('utf-8'), sheet.row(row_no))
                    else:
                        line = list(
                            map(lambda row: isinstance(row.value, bytes) and row.value.encode('utf-8') or str(
                                row.value),
                                sheet.row(row_no)))
                        a1 = int(float(line[10]))
                        a1_as_datetime = datetime(*xlrd.xldate_as_tuple(a1, workbook.datemode))
                        date_string = a1_as_datetime.date().strftime('%Y-%m-%d')
                        values = {'order': line[0],
                                  'customer': line[1],
                                  'pricelist': line[2],
                                  'product': line[3].split('.0')[0] if line[3].endswith('.0') else line[3],
                                  'quantity': line[4],
                                  'uom': line[5],
                                  'description': line[6],
                                  'price': line[7],
                                  'user': line[8],
                                  'tax': line[9],
                                  'date': date_string,
                                  'discount': line[11],
                                  'access_unit': line[12],
                                  'product_category': line[13],
                                  'seq_opt': self.sequence_opt,
                                  'vendor': line[14],
                                  'vendor_price': line[15]
                                  }
                        product_lines.append(values)
                self.make_sale_order(product_lines)

            else:
                for row_no in range(sheet.nrows):
                    if row_no <= 0:
                        fields = map(lambda row: row.value.encode('utf-8'), sheet.row(row_no))
                    else:
                        line = list(
                            map(lambda row: isinstance(row.value, bytes) and row.value.encode('utf-8') or str(
                                row.value),
                                sheet.row(row_no)))
                        a1 = int(float(line[10]))
                        a1_as_datetime = datetime(*xlrd.xldate_as_tuple(a1, workbook.datemode))
                        date_string = a1_as_datetime.date().strftime('%Y-%m-%d')
                        values.update({'order': line[0],
                                       'customer': line[1],
                                       'pricelist': line[2],
                                       'product': line[3].split('.0')[0] if line[3].endswith('.0') else line[3],
                                       'quantity': line[4],
                                       'uom': line[5],
                                       'description': line[6],
                                       'price': line[7],
                                       'user': line[8],
                                       'tax': line[9],
                                       'date': date_string,
                                       'discount': line[11],
                                       'access_unit': line[12],
                                       'product_category': line[13],
                                       'seq_opt': self.sequence_opt,
                                       'vendor': line[14],
                                       'vendor_price': line[15]
                                       })

                        res = self.make_sale(values)
                        sale_ids.append(res)

                if self.stage == 'confirm':
                    for res in sale_ids:
                        if res.state in ['draft', 'sent']:
                            res.action_confirm()

                return res

    def find_currency(self, name):
        currency_obj = self.env['product.pricelist']
        currency_search = currency_obj.search([('name', '=', name)], limit=1)

        if not currency_search:
            raise UserError(_('Pricelist "%s" is not available.') % name)

        return currency_search

    def make_sale_order(self, order_line):
        for i in range(0, len(order_line)):
            name = self.env['ir.sequence'].next_by_code('sale.order')

            partner_id = self.find_partner(order_line[i].get('customer'))
            currency_id = self.find_currency(order_line[i].get('pricelist'))
            user_id = self.find_user(order_line[i].get('user'))
            order_date = self.make_order_date(order_line[i].get('date'))

            sale_vals = {
                'partner_id': partner_id.id,
                'pricelist_id': currency_id.id,
                'name': name,
                'user_id': user_id.id,
                'date_order': order_date,
                'custom_seq': True if order_line[i].get('seq_opt') == 'custom' else False,
                'system_seq': True if order_line[i].get('seq_opt') == 'system' else False,
                'sale_name': order_line[i].get('order')
            }

            sale_id = self.env['sale.order'].create(sale_vals)
            break
        product_obj = self.env['product.product']
        for j in range(0, len(order_line)):
            if self.import_prod_option == 'barcode':
                product_search = product_obj.search([('barcode', '=', order_line[j]['product'])])
            elif self.import_prod_option == 'code':
                product_search = product_obj.search([('default_code', '=', order_line[j]['product'])], limit=1)
            else:
                product_search = product_obj.search([('name', '=', order_line[j]['product'])])

            product_uom = self.env['uom.uom'].search([('name', '=', order_line[j].get('uom'))])
            unit_id = self.env['access.units'].search([('name', '=', order_line[j].get('access_unit'))])
            product_category = self.env['product.category'].search(
                [('name', '=', order_line[j].get('product_category'))])
            vendor = self.env['res.partner'].search(
                [('name', '=', order_line[j].get('vendor'))])


            if product_uom.id == False:
                raise UserError(_('%s Product UOM category is not available.') % order_line[j].get('uom'))
            if not unit_id:
                unit_id = self.env['access.units'].create({
                    'name': order_line[j].get('access_unit'),
                })

            if not product_category:
                product_category = self.env['product.category'].create({
                    'name': order_line[j].get('product_category'),
                })
            if not vendor:
                vendor = self.env['res.partner'].create({
                    'name': order_line[j].get('vendor'),
                })
            if product_search:
                self.env['sale.order.line'].create({
                    'order_id': sale_id.id,
                    'product_id': product_search.id,
                    'name': product_search.name,
                    'product_uom_qty': order_line[j].get('quantity'),
                    'product_uom': product_uom.id,
                    'price_unit': order_line[j].get('price'),
                    'discount': order_line[j].get('discount'),
                    'vendor_id': vendor.id,
                    'vendor_price': order_line[j].get('vendor_price')
                })
            else:
                if self.import_prod_option == 'name':
                    product_id = product_obj.create({
                        'name': order_line[j].get('product'),
                        'lst_price': float(order_line[j].get('price')),
                        'uom_id': product_uom.id,
                        'uom_po_id': product_uom.id,
                        'unit_id': unit_id.id,
                        'categ_id': product_category.id,
                        'type': 'consu',

                    })
                    self.env['sale.order.line'].create({
                        'order_id': sale_id.id,
                        'product_id': product_id.id,
                        'name': product_id.name,
                        'product_uom_qty': order_line[j].get('quantity'),
                        'product_uom': product_uom.id,
                        'price_unit': order_line[j].get('price'),
                        'discount': order_line[j].get('discount'),
                        'vendor_id': vendor.id,
                        'vendor_price': order_line[j].get('vendor_price')
                    })

                elif self.import_prod_option == 'code':
                    product_id = product_obj.create({
                        'name': order_line[j].get('description'),
                        'lst_price': float(order_line[j].get('price')),
                        'uom_id': product_uom.id,
                        'uom_po_id': product_uom.id,
                        'default_code': order_line[j].get('product'),
                        'unit_id': unit_id.id,
                        'categ_id': product_category.id,
                        'type': 'consu',

                    })
                    self.env['sale.order.line'].create({
                        'order_id': sale_id.id,
                        'product_id': product_id.id,
                        'name': product_id.name,
                        'product_uom_qty': order_line[j].get('quantity'),
                        'product_uom': product_uom.id,
                        'price_unit': order_line[j].get('price'),
                        'discount': order_line[j].get('discount'),
                        'vendor_id': vendor.id,
                        'vendor_price': order_line[j].get('vendor_price')

                    })
                else:
                    raise UserError(
                        _('%s product is not found" .\n If you want to create product then first select Import '
                          'Product By Name option .') %
                        order_line[j].get(
                            'product'))
        if self.stage == 'confirm':
            if sale_id.state in ['draft', 'sent']:
                sale_id.action_confirm()
