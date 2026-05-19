import tempfile
import binascii
import xlrd
from datetime import datetime
from odoo import models, _, fields, exceptions

import logging

from odoo.exceptions import UserError

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


class GenPurchaseWithLot(models.TransientModel):
    _name = "gen.purchase_with_lot"

    file = fields.Binary('File')
    sequence_opt = fields.Selection(
        [('custom', 'Use Excel/CSV Sequence Number'), ('system', 'Use System Default Sequence Number')],
        string='Sequence Option', default='custom')
    import_option = fields.Selection([('xls', 'XLS File')], string='Select', default='xls')
    import_prod_option = fields.Selection([('code', 'Code'), ('barcode', 'Barcode'),('name', 'Name')],
                                          string='Import Product By ', default='code')
    stage = fields.Selection(
        [('draft', 'Import Draft Purchase'), ('confirm', 'Confirm Purchase Automatically With Import')],
        string="Purchase Stage Option", default='draft')

    def import_xls_of_po_with_lot(self):
        """Load Inventory data from the CSV file."""
        if not self.file:
            raise exceptions.UserError(
                _("No file uploaded. Please select a file to import."))
        if self.import_option == 'xls':
            fp = tempfile.NamedTemporaryFile(delete=False, suffix=".xlsx")
            fp.write(binascii.a2b_base64(self.file))
            fp.seek(0)
            values = {}
            purchase_ids = []
            workbook = xlrd.open_workbook(fp.name)
            sheet = workbook.sheet_by_index(0)
            product_lines = []
            if self.sequence_opt == 'system':
                date_string = False
                for row_no in range(sheet.nrows):
                    val = {}
                    tax_line = ''
                    if row_no <= 0:
                        fields = map(lambda row: row.value.encode('utf-8'), sheet.row(row_no))
                    else:
                        line = list(
                            map(lambda row: isinstance(row.value, bytes) and row.value.encode('utf-8') or str(
                                row.value),
                                sheet.row(row_no)))
                        if line[9] != '':
                            a1 = int(float(line[9]))
                            a1_as_datetime = datetime(*xlrd.xldate_as_tuple(a1, workbook.datemode))
                            date_string = a1_as_datetime.date().strftime('%Y-%m-%d')
                        if line[12] != '':
                            date_alert_date = False
                            date_use_date = False
                            if line[13]:
                                a2 = int(float(line[13]))
                                a2_as_datetime = datetime(*xlrd.xldate_as_tuple(a2, workbook.datemode))
                                date_use_date = a2_as_datetime.date().strftime('%Y-%m-%d')
                            if line[14]:
                                a3 = int(float(line[14]))
                                a3_as_datetime = datetime(*xlrd.xldate_as_tuple(a3, workbook.datemode))
                                date_alert_date = a3_as_datetime.date().strftime('%Y-%m-%d')

                            values = {'purchase_no': line[0],
                                      'vendor': line[1],
                                      'currency': line[2],
                                      'product': line[3].split('.0')[0] if line[3].endswith('.0') else line[3],
                                      'quantity': line[4],
                                      'uom': line[5],
                                      'description': line[6],
                                      'price': line[7],
                                      'tax': line[8],
                                      'date': date_string,
                                      'access_unit': line[10],
                                      'product_category': line[11],
                                      'seq_opt': self.sequence_opt,
                                      'lot_id': line[12].split('.0')[0] if line[12].endswith('.0') else line[12],
                                      'use_date': date_use_date,
                                      'alert_date': date_alert_date,
                                      }
                        else:
                            values = {'purchase_no': line[0],
                                      'vendor': line[1],
                                      'currency': line[2],
                                      'product': line[3].split('.0')[0] if line[3].endswith('.0') else line[3],
                                      'quantity': line[4],
                                      'uom': line[5],
                                      'description': line[6],
                                      'price': line[7],
                                      'tax': line[8],
                                      'date': date_string,
                                      'access_unit': line[10],
                                      'product_category': line[11],
                                      'seq_opt': self.sequence_opt,
                                      }
                        product_lines.append(values)
                self.make_purchase_order(product_lines)
            else:
                product_obj = self.env['product.product']
                date_string = False
                for row_no in range(sheet.nrows):
                    val = {}
                    tax_line = ''
                    if row_no <= 0:
                        fields = map(lambda row: row.value.encode('utf-8'), sheet.row(row_no))
                    else:
                        line = list(
                            map(lambda row: isinstance(row.value, bytes) and row.value.encode('utf-8') or str(
                                row.value),
                                sheet.row(row_no)))
                        if line[9] != '':
                            a1 = int(float(line[9]))
                            a1_as_datetime = datetime(*xlrd.xldate_as_tuple(a1, workbook.datemode))
                            date_string = a1_as_datetime.date().strftime('%Y-%m-%d')
                        if len(line) > 12 and line[12] != '':
                            date_alert_date = False
                            date_use_date = False

                            if line[13]:
                                a2 = int(float(line[13]))
                                a2_as_datetime = datetime(*xlrd.xldate_as_tuple(a2, workbook.datemode))
                                date_use_date = a2_as_datetime.date().strftime('%Y-%m-%d')
                            if line[14]:
                                a3 = int(float(line[14]))
                                a3_as_datetime = datetime(*xlrd.xldate_as_tuple(a3, workbook.datemode))
                                date_alert_date = a3_as_datetime.date().strftime('%Y-%m-%d')
                            values.update({'purchase_no': line[0],
                                           'vendor': line[1],
                                           'currency': line[2],
                                           'product': line[3].split('.0')[0] if line[3].endswith('.0') else line[3],
                                           'quantity': line[4],
                                           'uom': line[5],
                                           'description': line[6],
                                           'price': line[7],
                                           'tax': line[8],
                                           'date': date_string,
                                           'access_unit': line[10],
                                           'product_category': line[11],
                                           'seq_opt': self.sequence_opt,
                                           'lot_id': line[12].split('.0')[0] if line[12].endswith('.0') else line[12],
                                           'use_date': date_use_date,
                                           'alert_date': date_alert_date,
                                           })
                        else:
                            values.update({
                                'purchase_no': line[0] if len(line) > 0 else '',
                                'vendor': line[1] if len(line) > 1 else '',
                                'currency': line[2] if len(line) > 2 else '',
                                'product': (
                                    line[3].split('.0')[0] if len(line) > 3 and
                                                              line[3].endswith(
                                                                  '.0') else
                                    line[3]) if len(line) > 3 else '',
                                'quantity': line[4] if len(line) > 4 else 0,
                                'uom': line[5] if len(line) > 5 else '',
                                'description': line[6] if len(line) > 6 else '',
                                'price': line[7] if len(line) > 7 else 0.0,
                                'tax': line[8] if len(line) > 8 else '',
                                'date': date_string,
                                # Ensure `date_string` is already defined properly
                                'access_unit': line[10] if len(
                                    line) > 10 else '',
                                'product_category': line[11] if len(
                                    line) > 11 else '',
                                'seq_opt': self.sequence_opt,
                            })

                        res = self.make_purchase(values)
                        purchase_ids.append(res)

                if self.stage == 'confirm':
                    for res in purchase_ids:
                        if res.state in ['draft', 'sent']:
                            res.button_confirm()
                return res
        else:
            pass

    def make_purchase(self, values):
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
            else:
                pur_search = purchase_obj.search([
                    ('name', '=', values.get('purchase_no')),
                ])

        if pur_search:
            if pur_search.partner_id.name == values.get('vendor'):
                if pur_search.currency_id.name == values.get('currency'):
                    self.make_purchase_line(values, pur_search)
                    return pur_search
                else:
                    raise UserError(_('Currency is different for "%s" .\n Please define same.') % values.get('currency'))
            else:
                raise UserError(_('Customer name is different for "%s" .\n Please define same.') % values.get('vendor'))
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
                'custom_seq': True if values.get('seq_opt') == 'custom' else False,
                'system_seq': True if values.get('seq_opt') == 'system' else False,
                'purchase_name': values.get('purchase_no'),
                "picking_type_id": warehouse.in_type_id.id,
            })
        self.make_purchase_line(values, pur_id)
        return pur_id

    def make_purchase_line(self, values, pur_id):
        product_obj = self.env['product.product']
        lot_obj = self.env['stock.lot']
        account = False
        purchase_line_obj = self.env['purchase.order.line']
        current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        if self.import_prod_option == 'barcode':
            product_search = product_obj.search([('barcode', '=', values['product'])])
        elif self.import_prod_option == 'code':
            product_search = product_obj.search([('default_code', '=', values['product'])], limit=1)
        else:
            product_search = product_obj.search([('name', '=', values['product'])])
        product_uom = self.env['uom.uom'].search([('name', '=ilike', values.get('uom'))])
        unit_id = self.env['access.units'].search([('name', '=', values.get('access_unit'))])
        product_category = self.env['product.category'].search([('name', '=', values.get('product_category'))])

        if product_uom.id == False:
            raise UserError(_(' %s Product UOM category is not available.') % values.get('uom'))
        if not unit_id:
            unit_id = self.env['access.units'].create({
                'name': values.get('access_unit'),
            })

        if not product_category:
            product_category = self.env['product.category'].create({
                'name': values.get('product_category'),
            })
        if product_search:
            product_id = product_search
        else:
            if self.import_prod_option == 'name':
                product_id = product_obj.create({
                    'name': values.get('product'),
                    'lst_price': float(values.get('price')),
                    'uom_id': product_uom.id,
                    'uom_po_id': product_uom.id,
                    'unit_id': unit_id.id,
                    'categ_id': product_category.id,
                    'type': 'consu',
                })
            elif self.import_prod_option == 'code':
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
            if values.get('lot_id'):
                use_date = False
                alert_date = False
                if values.get('alert_date'):
                    alert_date = self.make_purchase_date(values.get('alert_date'))
                if values.get('use_date'):
                    use_date = self.make_purchase_date(values.get('use_date'))
                lot_search = lot_obj.search([('name', '=', values['lot_id']), ('product_id', '=', product_search.id)], limit=1)
                if lot_search:
                    stock_production_lot = lot_search
                else:
                    stock_production_lot = self.env['stock.lot'].create(
                        {
                            'name': values.get('lot_id'),
                            'product_id': product_search.id,
                            'product_qty': float(values.get('quantity')),
                            'po_line_id': po_order_lines.id,
                            'company_id': pur_id.company_id.id,
                            'life_date': use_date,
                            'alert_date': alert_date,
                        }
                    )
                purchase_product_lot = self.env['purchase.product.lot']
                if stock_production_lot:
                    po_order_lines.purchase_product_lot_ids = [(4, purchase_product_lot.create({
                        'name': stock_production_lot.name,
                        'po_line_id': stock_production_lot.po_line_id.id,
                        'product_uom_id': stock_production_lot.po_line_id.product_uom.id,
                        'product_qty': values.get('quantity'),
                        'company_id': stock_production_lot.company_id.id,
                        'lot_id': stock_production_lot.id,
                        'use_date': use_date,
                    }).id)]
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
            raise UserError(_('We cannot import data in validated or confirmed order.'))

        tax_ids = []
        if values.get('tax'):
            if ';' in values.get('tax'):
                tax_names = values.get('tax').split(';')
                for name in tax_names:
                    tax = self.env['account.tax'].search([('name', '=', name), ('type_tax_use', '=', 'purchase')])
                    if not tax:
                        raise UserError(_('"%s" Tax not in your system') % name)
                    tax_ids.append(tax.id)

            elif ',' in values.get('tax'):
                tax_names = values.get('tax').split(',')
                for name in tax_names:
                    tax = self.env['account.tax'].search([('name', '=', name), ('type_tax_use', '=', 'purchase')])
                    if not tax:
                        raise UserError(_('"%s" Tax not in your system') % name)
                    tax_ids.append(tax.id)
            else:
                tax_names = values.get('tax').split(',')
                for name in tax_names:
                    tax = self.env['account.tax'].search([('name', '=', name), ('type_tax_use', '=', 'purchase')])
                    if not tax:
                        raise UserError(_('"%s" Tax not in your system') % name)
                    tax_ids.append(tax.id)

        if tax_ids:
            po_order_lines.write({'taxes_id': ([(6, 0, tax_ids)])})

        return True

    def find_partner(self, name):
        partner_obj = self.env['res.partner']
        partner_search = partner_obj.search([('name', '=', name)])
        if partner_search:
            return partner_search
        else:
            partner_id = partner_obj.create({
                'name': name})
            return partner_id

    def find_currency(self, name):
        currency_obj = self.env['res.currency']
        currency_search = currency_obj.search([('name', '=', name)])
        if currency_search:
            return currency_search
        else:
            raise UserError(_(' "%s" Currency are not available.') % name)

    def make_purchase_date(self, date):
        DATETIME_FORMAT = "%Y-%m-%d"
        i_date = datetime.strptime(date, DATETIME_FORMAT)
        return i_date

    def make_purchase_order(self, order_line):
        for i in range(0, len(order_line)):
            name = self.env['ir.sequence'].next_by_code('purchase.order')
            partner_id = self.find_partner(order_line[i].get('vendor'))
            currency_id = self.find_currency(order_line[i].get('currency'))
            if order_line[i].get('date'):
                pur_date = self.make_purchase_date(order_line[i].get('date'))
            else:
                pur_date = datetime.today()

            purchase_vals = {
                'partner_id': partner_id.id,
                'currency_id': currency_id.id,
                'name': name,
                'date_order': pur_date,
                'custom_seq': True if order_line[i].get('seq_opt') == 'custom' else False,
                'system_seq': True if order_line[i].get('seq_opt') == 'system' else False,
                'purchase_name': order_line[i].get('purchase_no')
            }
            purchase_id = self.env['purchase.order'].create(purchase_vals)
            break
        current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        product_obj = self.env['product.product']
        lot_obj = self.env['stock.lot']
        for j in range(0, len(order_line)):
            if self.import_prod_option == 'barcode':
                product_search = product_obj.search([('barcode', '=', order_line[j]['product'])])
            elif self.import_prod_option == 'code':
                product_search = product_obj.search([('default_code', '=', order_line[j]['product'])], limit=1)
            else:
                product_search = product_obj.search([('name', '=', order_line[j]['product'])])
            product_uom = self.env['uom.uom'].search([('name', '=ilike', order_line[j].get('uom'))])
            unit_id = self.env['access.units'].search([('name', '=', order_line[j].get('access_unit'))])
            product_category = self.env['product.category'].search(
                [('name', '=', order_line[j].get('product_category'))])

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
            if product_search:

                po_line_id = self.env['purchase.order.line'].create({
                    'order_id': purchase_id.id,
                    'product_id': product_search.id,
                    'name': product_search.name,
                    'date_planned': current_time,
                    'product_qty': order_line[j].get('quantity'),
                    'product_uom': product_uom.id,
                    'price_unit': order_line[j].get('price')
                })
                if order_line[j].get('lot_id'):
                    use_date = False
                    alert_date = False
                    if order_line[j].get('alert_date'):
                        alert_date = self.make_purchase_date(order_line[j].get('alert_date'))
                    if order_line[j].get('use_date'):
                        use_date = self.make_purchase_date(order_line[j].get('use_date'))
                    lot_search = lot_obj.search(
                        [('name', '=', order_line[j]['lot_id']), ('product_id', '=', product_search.id)], limit=1)
                    if lot_search:
                        stock_production_lot = lot_search
                    else:
                        stock_production_lot = self.env['stock.lot'].create(
                            {
                                'name': order_line[j].get('lot_id'),
                                'product_id': product_search.id,
                                'product_qty': float(order_line[j].get('quantity')),
                                'po_line_id': po_line_id.id,
                                'company_id': purchase_id.company_id.id,
                                'life_date': use_date,
                                'alert_date': alert_date,
                            }
                        )
                    purchase_product_lot = self.env['purchase.product.lot']
                    if stock_production_lot:
                        po_line_id.purchase_product_lot_ids = [(4, purchase_product_lot.create({
                            'name': stock_production_lot.name,
                            'po_line_id': stock_production_lot.po_line_id.id,
                            'product_uom_id': stock_production_lot.po_line_id.product_uom.id,
                            'product_qty': order_line[j].get('quantity'),
                            'company_id': stock_production_lot.company_id.id,
                            'lot_id': stock_production_lot.id,
                            'use_date': use_date,
                        }).id)]

            else:
                if self.import_prod_option == 'name':
                    product_id = product_obj.create({
                        'name': order_line[j].get('product'),
                        'lst_price': float(order_line[j].get('price')),
                        'uom_id': product_uom.id,
                        'uom_po_id': product_uom.id,
                        'unit_id': unit_id.id,
                        'categ_id': product_category.id,
                    })
                    po_line_id = self.env['purchase.order.line'].create({
                        'order_id': purchase_id.id,
                        'product_id': product_id.id,
                        'name': product_id.name,
                        'date_planned': current_time,
                        'product_qty': order_line[j].get('quantity'),
                        'product_uom': product_uom.id,
                        'price_unit': order_line[j].get('price')
                    })
                    if order_line[j].get('lot_id'):
                        use_date = False
                        alert_date = False
                        if order_line[j].get('alert_date'):
                            alert_date = self.make_purchase_date(order_line[j].get('alert_date'))
                        if order_line[j].get('use_date'):
                            use_date = self.make_purchase_date(order_line[j].get('use_date'))
                        lot_search = lot_obj.search(
                            [('name', '=', order_line[j]['lot_id']), ('product_id', '=', product_search.id)], limit=1)
                        if lot_search:
                            stock_production_lot = lot_search
                        else:
                            stock_production_lot = self.env['stock.lot'].create(
                                {
                                    'name': order_line[j].get('lot_id'),
                                    'product_id': product_id.id,
                                    'product_qty': float(order_line[j].get('quantity')),
                                    'po_line_id': po_line_id.id,
                                    'company_id': purchase_id.company_id.id,
                                    'life_date': use_date,
                                    'alert_date': alert_date
                                }
                            )
                        purchase_product_lot = self.env['purchase.product.lot']
                        if stock_production_lot:
                            po_line_id.purchase_product_lot_ids = [(4, purchase_product_lot.create({
                                'name': stock_production_lot.name,
                                'po_line_id': stock_production_lot.po_line_id.id,
                                'product_uom_id': stock_production_lot.po_line_id.product_uom.id,
                                'product_qty': order_line[j].get('quantity'),
                                'company_id': stock_production_lot.company_id.id,
                                'lot_id': stock_production_lot.id,
                                'use_date': use_date,
                            }).id)]

                elif self.import_prod_option == 'code':
                    product_id = product_obj.create({
                        'name': order_line[j].get('description'),
                        'default_code': order_line[j].get('product'),
                        'lst_price': float(order_line[j].get('price')),
                        'uom_id': product_uom.id,
                        'uom_po_id': product_uom.id,
                        'unit_id': unit_id.id,
                        'categ_id': product_category.id,
                        'type': 'consu',
                    })
                    po_line_id = self.env['purchase.order.line'].create({
                        'order_id': purchase_id.id,
                        'product_id': product_id.id,
                        'name': product_id.name,
                        'date_planned': current_time,
                        'product_qty': order_line[j].get('quantity'),
                        'product_uom': product_uom.id,
                        'price_unit': order_line[j].get('price')
                    })

                    if order_line[j].get('lot_id'):
                        use_date = False
                        alert_date = False
                        if order_line[j].get('alert_date'):
                            alert_date = self.make_purchase_date(order_line[j].get('alert_date'))
                        if order_line[j].get('use_date'):
                            use_date = self.make_purchase_date(order_line[j].get('use_date'))
                        lot_search = lot_obj.search(
                            [('name', '=', order_line[j]['lot_id']), ('product_id', '=', product_search.id)], limit=1)
                        if lot_search:
                            stock_production_lot = lot_search
                        else:
                            stock_production_lot = self.env['stock.lot'].create(
                                {
                                    'name': order_line[j].get('lot_id'),
                                    'product_id': product_id.id,
                                    'product_qty': float(order_line[j].get('quantity')),
                                    'po_line_id': po_line_id.id,
                                    'company_id': purchase_id.company_id.id,
                                    'life_date': use_date,
                                    'alert_date': alert_date
                                }
                            )
                        purchase_product_lot = self.env['purchase.product.lot']
                        if stock_production_lot:
                            po_line_id.purchase_product_lot_ids = [(4, purchase_product_lot.create({
                                'name': stock_production_lot.name,
                                'po_line_id': stock_production_lot.po_line_id.id,
                                'product_uom_id': stock_production_lot.po_line_id.product_uom.id,
                                'product_qty': order_line[j].get('quantity'),
                                'company_id': stock_production_lot.company_id.id,
                                'lot_id': stock_production_lot.id,
                                'use_date': use_date,
                            }).id)]

                else:
                    raise UserError(
                        _('%s product is not found" .\n If you want to create product then first select Import '
                          'Product By Name option .') %
                        order_line[j].get(
                            'product'))

        if self.stage == 'confirm':
            if purchase_id.state in ['draft', 'sent']:
                purchase_id.button_confirm()
