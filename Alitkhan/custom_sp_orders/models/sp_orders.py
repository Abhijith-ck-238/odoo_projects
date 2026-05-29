# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class SpOrders(models.Model):
    _name = "sp.order"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = "SP Order"

    name = fields.Char("Order Number", readonly=True, default="New")
    employee_id = fields.Many2one('hr.employee', string="Employee")
    contract_id = fields.Many2one("contract.contract", string="Contract", tracking=True)
    product_line_ids = fields.One2many('sp.order.product.lines', 'sp_order_id', "Products")
    state = fields.Selection(selection=[('draft', 'Draft'), ('submit', 'Submitted'),
                                        ('ordering', 'Ordering'), ('delivered', 'Delivered')], default="draft", tracking=True)
    serial_number = fields.Char("Serial Number", tracking=True)
    po_count = fields.Integer(compute="compute_po_count")
    # name = fields.Char(string="Reference Number", default=lambda self: _('New'), readonly=True, copy=False)

    # @api.model
    # def create(self, vals):
    #     """Automatically generate a reference number for new books."""
    #     print("hyyyy")
    #     if vals.get('name', _('New')) == _('New'):
    #         vals['name'] = self.env['ir.sequence'].next_by_code('sp.order')
    #     return super(SpOrders, self).create(vals)

    # print("lll",lambda self: self.env.user.employee_id)

    @api.onchange('serial_number')
    def onchange_serial_number(self):
        if self.serial_number:
            contract_product = self.env['contract.product'].search([('sn', '=', self.serial_number)])
            if contract_product:
                self.contract_id = contract_product.contract_id


    @api.model
    def create(self, vals_list):
        if vals_list.get('name', _('New')) == _('New'):
            vals_list['name'] = self.env['ir.sequence'].next_by_code(
                'sp.orders.seq') or _('New')
            res = super(SpOrders, self).create(vals_list)
        return res


    def action_submit(self):
        users = self.env.ref("custom_sp_orders.group_sp_orders_administrator").users
        for user in users:
            self.env['mail.activity'].create({
                'display_name': 'Sp Order Submitted',
                'summary': 'Sp Order Submitted',
                'note': 'Sp Order is submitted by the employee ' + self.employee_id.name + '.',
                'date_deadline': fields.datetime.now(),
                'user_id': user.id,
                'res_id': self.id,
                'res_model_id': self.env['ir.model'].sudo().search(
                    [('model', '=', 'sp.order')], limit=1).id,
                'activity_type_id': self.env.ref("custom_sp_orders.mail_activity_sp_orders").id
            })
        self.write({
            'state': 'submit'
        })

    def action_reset_draft(self):
        self.write({
            'state': 'draft'
        })
        self.activity_ids.action_done()

    def action_move_to_ordering(self):
        self.write({
            'state': 'ordering'
        })
        self.activity_ids.action_done()

    def action_delivered(self):
        self.write({
            'state': 'delivered'
        })
        self.activity_ids.action_done()
        self.env['mail.activity'].create({
            'display_name': 'Sp Order Submitted',
            'summary': 'Sp Order Submitted',
            'note': 'Sp Order '+ self.name + ' is delivered.',
            'date_deadline': fields.datetime.now(),
            'user_id': self.employee_id.user_id.id if self.employee_id.user_id else self.env.user.id,
            'res_id': self.id,
            'res_model_id': self.env['ir.model'].sudo().search(
                [('model', '=', 'sp.order')], limit=1).id,
            'activity_type_id': self.env.ref(
                "custom_sp_orders.mail_activity_sp_orders").id
        })

    def action_create_po(self):
        return {
            'name': _('Purchase Order'),
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'purchase.order',
            'target': 'new',
            'context':{'default_order_line': [((0, 0, {
                    'product_id': p.product_id.id,
                    'name':p.product_id.name,
                    'product_qty': p.quantity}) )for p in self.product_line_ids],
                       'default_sp_order_id': self.id},
        }

    def action_purchase_order(self):
        return {
            "type": "ir.actions.act_window",
            "res_model": "purchase.order",
            "views": [[False, "list"],
                      [False, "form"]],
            "domain": [("sp_order_id", "=", self.id)],
            "context": dict(self._context, create=False),
            "name": "Purchase Order",
        }

    def compute_po_count(self):
        for rec in self:
            purchase_order_count = self.env['purchase.order'].search_count([('sp_order_id', '=', rec.id)])
            rec.po_count =purchase_order_count
