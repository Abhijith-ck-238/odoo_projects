from odoo import models, fields, api


class OfferingConfigLineExtend(models.Model):
    _inherit = 'offering.config.line'
    _description = 'Offering Config Line'

    product_access_unit = fields.Many2one('access.units', string="Access Unit")
    exchange_rate = fields.Float(string="Exchange rate")
    total_price = fields.Float(string="PO Price",
                               groups="itkan_offering.offering_user,itkan_offering.offering_manager")
    so_total_price = fields.Float(string="SO Price",
                                  groups="itkan_offering.offering_user,itkan_offering.offering_manager")
    uom_id = fields.Many2one('uom.uom', 'UOM')


class OfferingConfigExtend(models.Model):
    _inherit = 'offering.config'
    _description = 'Offering Config'

    @api.depends("product_bom_lines")
    def _get_vendor_price(self):
        for config in self:
            config = config.sudo()
            vendor_price = 0
            for line in config.product_bom_lines:
                vendor_price += line.total_price
            config.total_vendor_price = vendor_price
