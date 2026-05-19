# -*- coding: utf-8 -*-
from odoo import fields, models, api, Command,_


class IrModelAccess(models.Model):
    _inherit = 'ir.model.access'

    def update_access_rights(self, access_rights_data):
        for access in self:
            access_right = next((access_data for access_data in access_rights_data if access_data.get('id') == access.id), None)
            if access_right:
                access.update({
                    'name': access_right['name'],
                    'group_id': access_right['group_id'][0],
                    'perm_read': access_right['perm_read'],
                    'perm_write': access_right['perm_write'],
                    'perm_create': access_right['perm_create'],
                    'perm_unlink': access_right['perm_unlink']
                })



