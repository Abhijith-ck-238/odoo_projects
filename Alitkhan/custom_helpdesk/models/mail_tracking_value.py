# Part of Odoo. See LICENSE file for full copyright and licensing details.

from datetime import datetime

from odoo import api, fields, models



class MailTrackingValues(models.Model):
    """Updated to fix the issue occurred while updating stage form resources to 'in progress'"""
    _inherit = 'mail.tracking.value'

    @api.model
    def _create_tracking_values(self, initial_value, new_value, col_name, col_info, record):
        """ Prepare values to create a mail.tracking.value. It prepares old and
        new value according to the field type.

        :param initial_value: field value before the change, could be text, int,
          date, datetime, ...;
        :param new_value: field value after the change, could be text, int,
          date, datetime, ...;
        :param str col_name: technical field name, column name (e.g. 'user_id);
        :param dict col_info: result of fields_get(col_name);
        :param <record> record: record on which tracking is performed, used for
          related computation e.g. finding currency of monetary fields;

        :return: a dict values valid for 'mail.tracking.value' creation;
        """
        field = self.env['ir.model.fields']._get(record._name, col_name)
        if not field:
            raise ValueError(f'Unknown field {col_name} on model {record._name}')

        values = {'field_id': field.id}
        if col_info['type'] in {'integer', 'float', 'char', 'text', 'datetime'}:
            values.update({
                f'old_value_{col_info["type"]}': initial_value,
                f'new_value_{col_info["type"]}': new_value
            })
        elif col_info['type'] == 'monetary':
            values.update({
                'currency_id': record[col_info['currency_field']].id,
                'old_value_float': initial_value,
                'new_value_float': new_value
            })
        elif col_info['type'] == 'date':
            values.update({
                'old_value_datetime': initial_value and fields.Datetime.to_string(
                    datetime.combine(fields.Date.from_string(initial_value), datetime.min.time())) or False,
                'new_value_datetime': new_value and fields.Datetime.to_string(
                    datetime.combine(fields.Date.from_string(new_value), datetime.min.time())) or False,
            })
        elif col_info['type'] == 'boolean':
            values.update({
                'old_value_integer': initial_value,
                'new_value_integer': new_value
            })
        elif col_info['type'] == 'selection':
            values.update({
                'old_value_char': initial_value and dict(col_info['selection']).get(initial_value, initial_value) or '',
                'new_value_char': new_value and dict(col_info['selection'])[new_value] or ''
            })
        elif col_info['type'] == 'many2one':
            values.update({
                'old_value_integer': initial_value.id if initial_value else 0,
                'new_value_integer': new_value.id if new_value else 0,
                'old_value_char': initial_value.display_name if initial_value else '',
                'new_value_char': new_value.display_name if new_value else ''
            })
        elif col_info['type'] in {'one2many', 'many2many'}:
            old_names = [name for name in initial_value.mapped('display_name') if name]
            new_names = [name for name in new_value.mapped('display_name') if name]
            values.update({
                'old_value_char': ', '.join(old_names) if old_names else '',
                'new_value_char': ', '.join(new_names) if new_names else '',
            })
        elif field.name != "duration_tracking" and field.model != 'helpdesk.ticket':
            raise NotImplementedError(f'Unsupported tracking on field {field.name} (type {col_info["type"]}')

        return values
