# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.
import tempfile
import binascii
import xlrd
import io
from datetime import date, datetime
from odoo.exceptions import UserError
from odoo import models, fields, exceptions, api, _

import logging
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

class GenPurchase(models.TransientModel):
    _name = "gen.purchase"

    file = fields.Binary('File')
    sequence_opt = fields.Selection(
        [('custom', 'Use Excel/CSV Sequence Number'),
         ('system', 'Use System Default Sequence Number')],
        string='Sequence Option', default='custom')
    import_option = fields.Selection([('xls', 'XLS File')], string='Select',
                                     default='xls')
    stage = fields.Selection(
        [('draft', 'Import Draft Purchase'),
         ('confirm', 'Confirm Purchase Automatically With Import')],
        string="Purchase Stage Option", default='draft')
    import_prod_option = fields.Selection(
        [('code', 'Code'), ('barcode', 'Barcode'), ('name', 'Name')],
        string='Import Product By ', default='code')

    def make_purchase(self, values):
        """ Make Purchase order"""
        purchase_obj = self.env['purchase.order']
        if self.sequence_opt == "custom":
            if values.get('purchase_no') == '':
                raise UserError(
                    _('You must set a Purchase order number on the excel sheet or choose the sequence option '
                      'as \' Use System Default Sequence Number \' to import the Purchase Order.'))
            pur_search = purchase_obj.search([
                ('name', '=', values.get('purchase_no')),
            ])
        else:
            if values.get('purchase_no') == '':
                pur_search = False
            pur_search = purchase_obj.search([
                ('purchase_name', '=', values.get('purchase_no')),
            ])
        if pur_search:
            if pur_search.partner_id.name == values.get('vendor'):
                if pur_search.currency_id.name == values.get('currency'):
                    self.make_purchase_line(values, pur_search)
                    return pur_search
                else:
                    raise UserError(
                        _('Currency is different for "%s" .\n Please define same.') % values.get(
                            'currency'))
            else:
                raise UserError(
                    _('Customer name is different for "%s" .\n Please define same.') % values.get(
                        'vendor'))
        else:
            if values.get('seq_opt') == 'system':
                name = self.env['ir.sequence'].next_by_code('purchase.order')
            elif values.get('seq_opt') == 'custom':
                name = values.get('purchase_no')
            partner_id = self.find_partner(values.get('vendor'))
            currency_id = self.find_currency(values.get('currency'))
            if values.get('date'):
                pur_date = self.make_purchase_date(values.get('date'))
            else:
                pur_date = datetime.today()
            # Dynamically find the default warehouse and its picking type
            warehouse = self.env['stock.warehouse'].search([],
                                                           limit=1)  # Get the first warehouse
            if not warehouse:
                raise UserError(
                    _('No warehouse found in the system. Please configure at least one warehouse.'))
            pur_id = purchase_obj.create({
                'partner_id': partner_id.id,
                'currency_id': currency_id.id,
                'name': name,
                'date_order': pur_date,
                'custom_seq': True if values.get(
                    'seq_opt') == 'custom' else False,
                'system_seq': True if values.get(
                    'seq_opt') == 'system' else False,
                'purchase_name': values.get('purchase_no'),
                "picking_type_id": warehouse.in_type_id.id,

            })
        self.make_purchase_line(values, pur_id)
        return pur_id

    def make_purchase_date(self, date):
        DATETIME_FORMAT = "%Y-%m-%d"
        i_date = datetime.strptime(date, DATETIME_FORMAT)
        return i_date

    def make_purchase_line(self, values, pur_id):
        product_obj = self.env['product.product']
        account = False
        purchase_line_obj = self.env['purchase.order.line']
        current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        if self.import_prod_option == 'barcode':
            product_search = product_obj.search(
                [('barcode', '=', values['product'])])
        elif self.import_prod_option == 'code':
            product_search = product_obj.search(
                [('default_code', '=', values['product'])])
        else:
            product_search = product_obj.search(
                [('name', '=', values['product'])])
        # First try exact match on UOM
        product_uom = self.env['uom.uom'].search(
            [('name', '=', values.get('uom'))])
        # If no UOM found, try case insensitive search
        if not product_uom:
            product_uom = self.env['uom.uom'].search(
                [('name', 'ilike', values.get('uom'))])
        # If still no UOM found, try some common mappings
        if not product_uom:
            uom_mapping = {
                'Units': 'Unit',
                'units': 'Unit',
                'UNITS': 'Unit',
                'EA': 'Unit',
                'Each': 'Unit',
                'PCS': 'Unit'
            }
            mapped_uom = uom_mapping.get(values.get('uom'))
            if mapped_uom:
                product_uom = self.env['uom.uom'].search(
                    [('name', '=', mapped_uom)])
        if not product_uom:
            raise UserError(
                _('"%s" Product UOM category is not available. Please check if this UOM exists in your system.') % values.get(
                    'uom'))
        if product_search:
            product_id = product_search
        else:
            if self.import_prod_option == 'name':
                # Create the product with all necessary information
                product_id = product_obj.create({
                    'name': values.get('description'),
                    'default_code': values.get('product'),
                    'lst_price': float(values.get('price')),
                    'uom_id': product_uom.id,
                    'uom_po_id': product_uom.id,
                    # 'type': 'product',  # Storable product
                    'purchase_ok': True,
                    'sale_ok': True
                })
            else:
                raise UserError(
                    _('%s product is not found. If you want to create product then first select Import Product By Name option.') % values.get(
                        'product'))
        # Rest of the method remains the same
        if pur_id.state == 'draft':
            po_order_lines = purchase_line_obj.create({
                'order_id': pur_id.id,
                'product_id': product_id.id,
                'name': values.get('description'),
                'date_planned': current_time,
                'product_qty': values.get('quantity'),
                'product_uom': product_uom.id,
                'price_unit': values.get('price')
            })
        elif pur_id.state == 'sent':
            po_order_lines = purchase_line_obj.create({
                'order_id': pur_id.id,
                'product_id': product_id.id,
                'name': values.get('description'),
                'date_planned': current_time,
                'product_qty': values.get('quantity'),
                'product_uom': product_uom.id,
                'price_unit': values.get('price')
            })
        elif pur_id.state != 'sent' or pur_id.state != 'draft':
            raise UserError(
                _('We cannot import data in validated or confirmed order.'))
        # Process tax information
        tax_ids = []
        if values.get('tax'):
            if ';' in values.get('tax'):
                tax_names = values.get('tax').split(';')
                for name in tax_names:
                    tax = self.env['account.tax'].search(
                        [('name', '=', name.strip()),
                         ('type_tax_use', '=', 'purchase')])
                    if not tax:
                        # Try case insensitive search
                        tax = self.env['account.tax'].search(
                            [('name', 'ilike', name.strip()),
                             ('type_tax_use', '=', 'purchase')])
                    if not tax:
                        # Skip invalid taxes instead of raising error
                        _logger.warning(
                            _('Tax "%s" not found in your system - skipping') % name.strip())
                        continue
                    tax_ids.append(tax.id)
            elif ',' in values.get('tax'):
                tax_names = values.get('tax').split(',')
                for name in tax_names:
                    tax = self.env['account.tax'].search(
                        [('name', '=', name.strip()),
                         ('type_tax_use', '=', 'purchase')])
                    if not tax:
                        # Try case insensitive search
                        tax = self.env['account.tax'].search(
                            [('name', 'ilike', name.strip()),
                             ('type_tax_use', '=', 'purchase')])
                    if not tax:
                        # Skip invalid taxes instead of raising error
                        _logger.warning(
                            _('Tax "%s" not found in your system - skipping') % name.strip())
                        continue
                    tax_ids.append(tax.id)
            else:
                tax = self.env['account.tax'].search(
                    [('name', '=', values.get('tax').strip()),
                     ('type_tax_use', '=', 'purchase')])
                if not tax:
                    # Try case insensitive search
                    tax = self.env['account.tax'].search(
                        [('name', 'ilike', values.get('tax').strip()),
                         ('type_tax_use', '=', 'purchase')])
                if not tax:
                    # Skip invalid taxes instead of raising error
                    _logger.warning(
                        _('Tax "%s" not found in your system - skipping') % values.get(
                            'tax').strip())
                else:
                    tax_ids.append(tax.id)
        if tax_ids:
            po_order_lines.write({'taxes_id': [(6, 0, tax_ids)]})
        return True
    def find_currency(self, name):
        currency_obj = self.env['res.currency']
        currency_search = currency_obj.search([('name', '=', name)])
        if currency_search:
            return currency_search
        else:
            raise UserError(_(' "%s" Currency are not available.') % name)
    def find_partner(self, name):
        partner_obj = self.env['res.partner']
        partner_search = partner_obj.search([('name', '=', name)])
        if partner_search:
            return partner_search
        else:
            partner_id = partner_obj.create({
                'name': name})
            return partner_id
    def import_csv(self):
        """Load Inventory data from the CSV file."""
        if not self.file:
            raise exceptions.UserError(
                _("No file uploaded. Please select a file to import."))

        if self.import_option == 'csv':
            keys = ['purchase_no', 'vendor', 'currency', 'product', 'quantity',
                    'uom', 'description', 'price', 'tax', 'date']
            csv_data = base64.b64decode(self.file)
            data_file = io.StringIO(csv_data.decode("utf-8"))
            data_file.seek(0)
            file_reader = []
            purchase_ids = []
            csv_reader = csv.reader(data_file, delimiter=',')
            try:
                file_reader.extend(csv_reader)
            except Exception:
                raise exceptions.UserError(_("Invalid file!"))
            values = {}
            for i in range(len(file_reader)):
                #                val = {}
                field = list(map(str, file_reader[i]))
                values = dict(zip(keys, field))
                if values:
                    if i == 0:
                        continue
                    else:
                        values.update({'seq_opt': self.sequence_opt})
                        res = self.make_purchase(values)
                        purchase_ids.append(res)

            if self.stage == 'confirm':
                for res in purchase_ids:
                    if res.state in ['draft', 'sent']:
                        res.button_confirm()
        else:
            fp = tempfile.NamedTemporaryFile(delete=False, suffix=".xlsx")
            fp.write(binascii.a2b_base64(self.file))
            fp.seek(0)
            values = {}
            purchase_ids = []
            workbook = xlrd.open_workbook(fp.name)
            sheet = workbook.sheet_by_index(0)
            product_obj = self.env['product.product']
            date_string = False
            # Get header row to determine column positions
            header_row = sheet.row_values(0)

            # Find column indices (to handle flexible column positioning)
            col_purchase_id = header_row.index(
                "PURCHASE ID") if "PURCHASE ID" in header_row else 0
            col_supplier = header_row.index(
                "SUPPLIER") if "SUPPLIER" in header_row else 1
            col_currency = header_row.index(
                "CURRENCY") if "CURRENCY" in header_row else 2
            col_product = header_row.index(
                "PRODUCT") if "PRODUCT" in header_row else 3
            col_quantity = header_row.index(
                "QUANTITY") if "QUANTITY" in header_row else 4
            col_uom = header_row.index("UOM") if "UOM" in header_row else 5
            col_description = header_row.index(
                "DESCRIPTION") if "DESCRIPTION" in header_row else 6
            col_price = header_row.index(
                "PRICE") if "PRICE" in header_row else 7
            col_tax = header_row.index("TAX") if "TAX" in header_row else 8
            col_date = header_row.index("DATE") if "DATE" in header_row else 9

            for row_no in range(1, sheet.nrows):  # Start from 1 to skip header
                try:
                    line = sheet.row_values(row_no)

                    # Clean up and process values
                    purchase_no = str(line[col_purchase_id]).strip()
                    vendor = str(line[col_supplier]).strip()
                    currency = str(line[col_currency]).strip()
                    product_code = str(line[col_product]).strip().split('.')[
                        0]  # Remove decimal part if any

                    # Handle quantity - convert to float
                    quantity = float(line[col_quantity]) if isinstance(
                        line[col_quantity], (int, float)) else float(
                        line[col_quantity].replace(',', ''))

                    uom = str(line[col_uom]).strip()
                    # Map common UOM variations
                    uom_mapping = {
                        'Units': 'Unit',
                        'units': 'Unit',
                        'UNITS': 'Unit',
                        'EA': 'Unit',
                        'Each': 'Unit',
                        'PCS': 'Unit'
                    }
                    if uom in uom_mapping:
                        uom = uom_mapping[uom]

                    description = str(line[col_description]).strip()

                    # Handle price - remove currency symbols and convert to float
                    price_str = str(line[col_price]).strip()
                    price_str = price_str.replace('$', '').replace(',', '')
                    price = float(price_str)

                    tax = str(line[col_tax]).strip() if line[col_tax] else ''

                    # Handle date
                    date_string = None
                    if isinstance(line[col_date], float) and line[col_date] > 0:
                        # Handle Excel date format
                        date_tuple = xlrd.xldate_as_tuple(line[col_date],
                                                          workbook.datemode)
                        date_string = datetime(*date_tuple).strftime('%Y-%m-%d')
                    elif line[col_date]:
                        # Try to parse date string if it's not empty
                        try:
                            date_string = datetime.strptime(
                                str(line[col_date]).strip(),
                                '%Y-%m-%d').strftime('%Y-%m-%d')
                        except ValueError:
                            date_string = None

                    if not date_string:
                        date_string = datetime.now().strftime('%Y-%m-%d')

                    values = {
                        'purchase_no': purchase_no,
                        'vendor': vendor,
                        'currency': currency,
                        'product': product_code,
                        'quantity': quantity,
                        'uom': uom,
                        'description': description,
                        'price': price,
                        'tax': tax,
                        'date': date_string,
                        'seq_opt': self.sequence_opt
                    }

                    _logger.info(f"Processing row {row_no}: {values}")
                    res = self.make_purchase(values)
                    purchase_ids.append(res)

                except Exception as e:
                    _logger.error(f"Error processing row {row_no}: {str(e)}")
                    raise UserError(
                        _(f"Error processing row {row_no}: {str(e)}"))

            if self.stage == 'confirm':
                for res in purchase_ids:
                    if res.state in ['draft', 'sent']:
                        res.button_confirm()
        return res