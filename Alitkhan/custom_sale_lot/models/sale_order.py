from odoo import api, fields, models
from ast import literal_eval
import pytz
import json


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    product_unreserved_qty = fields.Float('Quantity', related='lot_id.product_unreserved_qty')
    use_date = fields.Datetime(string='Best before Date', related='lot_id.use_date')
    available_lot_ids = fields.Char(
        compute="compute_available_lot_ids",
        readonly=True,
        store=False,
    )

    @api.depends("product_id", "product_uom_qty")
    def compute_available_lot_ids(self):
        for rec in self:
            available_lot_ids = []
            if rec.order_id.warehouse_id and rec.product_id:
                location = rec.order_id.warehouse_id.lot_stock_id
                quants = self.env["stock.quant"].read_group(
                    [
                        ("product_id", "=", rec.product_id.id),
                        ("location_id", "child_of", location.id),
                        ("quantity", ">", 0),
                        ("lot_id", "!=", False),
                    ],
                    ["lot_id"],
                    "lot_id",
                )
                available_lot_ids = [quant["lot_id"][0] for quant in quants]
            rec.lot_id = False
            rec.available_lot_ids = json.dumps(
                [("id", "in", available_lot_ids), ('product_unreserved_qty', '>=', rec.product_uom_qty)]
            )


class SaleOrder(models.Model):
    _inherit = "sale.order"

    confirm_activity_ids = fields.Many2many('mail.activity', 'so_activity_rel', 'so_id', 'activity_id',
                                            string="SO Confirm Activities")

    def action_confirm(self):
        res = super(SaleOrder, self).action_confirm()
        users = self.env['ir.config_parameter'].sudo().get_param('sale.confirm_activity_user_ids')
        activity = self.env['mail.activity.type'].search([]).filtered(
            lambda m: m.name == "To Do"
        )
        for so in self:
            so_activity_ids = []
            for user_id in literal_eval(users):
                mail_activity = self.env['mail.activity'].create({
                    'res_id': so.id,
                    'res_model_id': self.env['ir.model'].sudo()._get('sale.order').id,
                    'activity_type_id': activity.id,
                    'summary': 'Invoice Creation Required',
                    'user_id': user_id,
                })
                so_activity_ids.append(mail_activity.id)
            so.write({'confirm_activity_ids': ([(6, 0, so_activity_ids)])})
        return res

    def notify_expire_alert_date(self):
        local_tz = pytz.timezone(self.env.user.tz if self.env.user.tz else self.env.context.get('tz') or pytz.utc)
        alert_users = self.env['ir.config_parameter'].sudo().get_param('sale.lot_expiry_alert_user_ids')
        activity = self.env['mail.activity.type'].search([]).filtered(
            lambda m: m.name == "To Do"
        )
        alert_lots = self.env['stock.lot'].sudo().search([]).filtered(
            lambda l: l.alert_date and l.alert_date.astimezone(local_tz).date() == fields.Date.today()
        )
        expire_lots = self.env['stock.lot'].sudo().search([]).filtered(
            lambda l: l.use_date and l.use_date.astimezone(local_tz).date() == fields.Date.today()
        )
        if alert_users:
            for user_id in literal_eval(alert_users):
                for alert_lot in alert_lots:
                    mail_activity = self.env['mail.activity'].create({
                        'res_id': alert_lot.id,
                        'res_model_id': self.env['ir.model'].sudo()._get('stock.lot').id,
                        'activity_type_id': activity.id,
                        'summary': 'Alert Date Reached!',
                        'user_id': user_id,
                    })
                for expire_lot in expire_lots:
                    mail_activity = self.env['mail.activity'].create({
                        'res_id': expire_lot.id,
                        'res_model_id': self.env['ir.model'].sudo()._get('stock.lot').id,
                        'activity_type_id': activity.id,
                        'summary': 'Expire Date Reached!',
                        'user_id': user_id,
                    })
