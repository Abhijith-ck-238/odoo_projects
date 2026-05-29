from odoo import fields, models


class ScanConfirmWizard(models.TransientModel):
    _name = "scan.confirm.wizard"
    _description = 'Scan Confirm wizard'

    msg = fields.Text(string="Confirm message",
                      default="Do you want to scan product?", readonly=True)

    def yes(self):
        transfer = self.env['stock.picking'].browse(self.env.context.get('active_id'))
        transfer.action_scan_product()

    def no(self):
        return False


class FetchConfirmWizard(models.TransientModel):
    _name = "fetch.confirm.wizard"
    _description = 'Fetch Confirm wizard'

    msg = fields.Text(string="Confirm message",
                      default="Do you want to fetch the RFID Quantity?", readonly=True)

    def yes(self):
        transfer = self.env['stock.picking'].browse(self.env.context.get('active_id'))
        res = transfer.action_fetch_rfid_data()
        return res

    def no(self):
        return False

class DoneConfirmWizard(models.TransientModel):
    _name = "done.confirm.wizard"
    _description = 'Done Confirm wizard'

    msg = fields.Text(string="Confirm message",
                      default="Do you want to Done the RFID Quantity?", readonly=True)

    def yes(self):
        print(self.env.context,'self.env.context')
        transfer = self.env['stock.picking'].browse(self.env.context.get('active_id'))
        transfer.action_rfid_done()

    def no(self):
        return False
