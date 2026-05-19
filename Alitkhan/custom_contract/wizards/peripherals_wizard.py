from odoo import models, fields


class PeripheralsWizard(models.TransientModel):
    _name = 'peripherals.wizard'

    contract_product_id = fields.Many2one('contract.product')
    peripherals = fields.Many2many('peripheral.peripheral', string='Peripherals')

    def save_peripherals(self):
        self.contract_product_id.peripherals = self.peripherals
