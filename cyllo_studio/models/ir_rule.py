# -*- coding: utf-8 -*-
from odoo import fields, models, api, Command


class IrModelAccess(models.Model):
    _inherit = 'ir.rule'

    def update_record_rules(self, record_rules):
        for record in self:
            record_rule = next((record_data for record_data in record_rules if record_data.get('id') == record.id), None)
            print("sample", record_rule)
            if record_rule:
                record.write({
                    'name': record_rule['name'],
                    'groups': record_rule['groups'],
                    'domain_force': record_rule['domain_force'],
                    'perm_read': record_rule['perm_read'],
                    'perm_write': record_rule['perm_write'],
                    'perm_create': record_rule['perm_create'],
                    'perm_unlink': record_rule['perm_unlink']
                })
