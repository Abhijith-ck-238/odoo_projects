from odoo import fields, models, _
from odoo.exceptions import UserError
import tempfile
import binascii
import xlrd
import base64


class ImportTechPolicies(models.Model):
    _name = 'import.tech.policies'
    _description = "Import Tech Policies"

    file = fields.Binary(string="Upload the XLSX file", required=True)

    def action_import_tech_policies(self):
        if not self.file:
            raise UserError(_('Please upload a file first.'))

        try:
            # Convert the file content to bytes
            file_data = base64.b64decode(self.file)

            # Create temporary file
            fp = tempfile.NamedTemporaryFile(delete=False, suffix=".xlsx")
            fp.write(file_data)
            fp.seek(0)

            # Open workbook and process data
            workbook = xlrd.open_workbook(fp.name)
            sheet = workbook.sheet_by_index(0)

            if sheet.nrows <= 1:
                raise UserError(_('File must contain at least one data row.'))

            for row_no in range(sheet.nrows):
                if row_no == 0:
                    # Verify header row
                    continue
                else:
                    try:
                        line = list(
                            map(lambda row: str(row.value), sheet.row(row_no)))

                        values = {
                            'name': line[1],
                            'date': line[2],
                            'authorized_person': line[3],
                            'example': line[4],
                            'note': line[5],
                        }

                        self.env['tech.policies'].create({
                            'name': values.get('name'),
                            'date': values.get('date'),
                            'authorized_person': values.get(
                                'authorized_person'),
                            'example': values.get('example'),
                            'notes': values.get('note'),
                        })
                    except Exception as e:
                        raise UserError(
                            _(f'Error processing row {row_no + 1}: {str(e)}'))

            # Return action to close wizard and show success message
            return {
                'type': 'ir.actions.client',
                'tag': 'reload',
                'params': {
                    'message': _(
                        'Tech policies have been successfully imported.'),
                    'type': 'success',
                }
            }

        except xlrd.XLRDError:
            raise UserError(
                _('Invalid file format. Please upload a valid XLSX file.'))
        except Exception as e:
            raise UserError(_(f'Error processing file: {str(e)}'))
        finally:
            fp.close()
