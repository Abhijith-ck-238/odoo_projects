from odoo import models, fields


class GenOffering(models.TransientModel):
    _name = "wizard.warning"
    _description = 'Display warning'

    purchase_link_id = fields.Many2one('link.purchase', string="Link id")
    msg = fields.Text(
        string="Warning",
        default="Some products unit price or total price is not matching with purchase order.Do You want to continue?",
        readonly=True)

    def yes(self):
        self.purchase_link_id.vendor_bill()
        return

    def no(self):
        self.purchase_link_id.link_purchase_order()
        return
