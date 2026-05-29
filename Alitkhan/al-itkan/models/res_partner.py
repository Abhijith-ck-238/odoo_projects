# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError

class ResPartner(models.Model):
    _inherit = "res.partner"

    # N.A Record id is => 25477
    # APIBOT user is => 64
    
    @api.model
    def create(self, values):
        """ Itakn DataBase is suffering from an issue with creating record.
        This function is to handle that error """
        na_record = self.env['res.partner'].browse([25477])
        api_id = 64
        if not values.get("name") and self.env.user.id == api_id:
            return na_record
        else:
            result = super(ResPartner, self).create(values)
            return result

    def unlink(self):
        for contact in self:
            if contact.id == 25477:
                raise UserError(_("You can not delete this contact cause it is being used by the support team"))
            else:
                pass

        res = super(ResPartner, self).unlink()
        return res

