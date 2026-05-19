from odoo import models, fields, _
import tempfile
import binascii
import xlrd
import re
from odoo.exceptions import ValidationError

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


class QrImportWizard(models.TransientModel):
    _name = "qr.import.wizard"
    _description = "Q&R Import Wizard"

    file = fields.Binary('File', required=True)

    def create_qr_import(self):
        qr_import = self.env['qr.import'].create({
            'user_id': self.env.user.id
        })
        return qr_import

    def import_xls(self):
        fp = tempfile.NamedTemporaryFile(delete=False, suffix=".xlsx")
        fp.write(binascii.a2b_base64(self.file))
        fp.seek(0)
        workbook = xlrd.open_workbook(fp.name)
        sheet = workbook.sheet_by_index(0)
        if sheet.ncols < 2:
            raise ValidationError("Too less columns to import")
        rec_import_vals = {
            'user_id': self.env.user.id
        }
        has_bad_refs = False
        has_bad_partners = False
        bad_refs = ""
        bad_partners = ""
        product_line_ids = []
        for row_no in range(sheet.nrows):
            vals_list = {}
            if row_no <= 0:
                sheet_fields = map(lambda row: row.value.encode('utf-8'), sheet.row(row_no))
            else:
                line = list(
                    map(lambda row: isinstance(row.value, bytes) and row.value.encode('utf-8') or str(
                        row.value),
                        sheet.row(row_no)))
                product = self.env['product.product'].search([]).filtered(
                    lambda p: p.default_code == line[0]
                )
                if not product:
                    product = self.env['product.product'].search(
                        [('default_code', '=ilike', line[0])], limit=1)
                if not product:
                    if re.findall(".", line[0]):
                        product = self.env['product.product'].search([]).filtered(
                            lambda p: p.default_code == line[0].split(".")[0]
                        )
                partner = self.env['res.partner'].sudo().search([
                    ('name', 'ilike', line[2])
                ], limit=1)
                vals_list.update(qty_required=line[1])
                if not product:
                    has_bad_refs = True
                    bad_refs += "%s , " % line[0]
                else:
                    vals_list.update(
                        product_id=product.id,
                        reserved_qty=product.reserved_qty,
                        qty_available=product.qty_available,
                        virtual_available=product.virtual_available,
                        free_available_qty=product.free_available_qty,
                        incoming_qty=product.incoming_qty

                    )
                if not partner:
                    has_bad_partners = True
                    bad_partners += "%s , " % line[2]
                else:
                    vals_list.update(required_partner_id=partner.id)
                product_line_ids.append((0, 0, vals_list))
        if has_bad_refs:
            raise ValidationError(_(
                "%s isn't found within Database."
                % bad_refs
            ))
        elif has_bad_partners:
            raise ValidationError(_(
                "Your sheet contains Contacts %s which are invalid."
                % bad_partners
            ))
        else:
            rec_import_vals.update(qr_product_ids=product_line_ids)
            rec_import = self.env['qr.import'].create(rec_import_vals)
            return {
                'name': _('Q&R Import'),
                'view_mode': 'form',
                'res_model': 'qr.import',
                'res_id': rec_import.id,
                'type': 'ir.actions.act_window',
                'target': 'main'
            }
