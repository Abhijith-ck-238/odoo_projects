from odoo import models, fields, api, _


class ProductReservation(models.Model):
    _name = "product.reservation"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = "Product Reservation"

    name = fields.Char("Reservation Number", readonly=True, default="New")
    employee_id = fields.Many2one(
        'hr.employee',
        string="Employee",
        default=lambda self: self.env['hr.employee'].search(
            [('user_id', '=', self.env.user.id)], limit=1).id or False,
        tracking=True
    )

    contract_id = fields.Many2one("contract.contract", string="Contract", tracking=True)
    product_line_ids = fields.One2many('product.lines', 'reservation_id', "Products", tracking=True)
    state = fields.Selection(selection=[('draft', 'Draft'), ('submit', 'Submitted'),
                                        ('reservation', 'Reservation')], default="draft", tracking=True)
    serial_number = fields.Char("Serial Number", tracking=True)
    is_return = fields.Boolean()

    @api.onchange('serial_number')
    def onchange_serial_number(self):
        if self.serial_number:
            contract_product = self.env['contract.product'].search([('sn', '=', self.serial_number)])
            if contract_product:
                self.contract_id = contract_product.contract_id

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if not vals.get('name') or vals.get('name') == _('New'):
                vals['name'] = self.env['ir.sequence'].next_by_code(
                    'product.reservation.seq') or _('New')
        return super().create(vals_list)

    def action_submit(self):

        # Get all users in the admin group
        users = self.env.ref(
            "custom_product_reservation.group_product_reservation_administrator").users

        # Get the res_model_id for 'product.reservation' using sudo to avoid access error
        model_id = self.env['ir.model'].sudo().search([
            ('model', '=', 'product.reservation')
        ], limit=1).id

        # Create an activity for each admin user
        for user in users:
            self.env['mail.activity'].sudo().create({
                'display_name': 'Product Reservation Submitted',
                'summary': 'Product Reservation Submitted',
                'note': 'Product reservation is submitted by the employee ' + str(
                    self.employee_id.name) + '.',
                'date_deadline': fields.datetime.now(),
                'user_id': user.id,
                'res_id': self.id,
                'res_model_id': model_id,  # Securely fetched using sudo
                'activity_type_id': self.env.ref(
                    "custom_product_reservation.mail_activity_product_reservation").id
            })

        # Change state to 'submit'
        self.write({
            'state': 'submit'
        })

    def action_reset_draft(self):
        self.write({
            'state': 'draft'
        })
        self.activity_ids.action_done()

    def action_reserve(self):
        self.write({
            'state': 'reservation'
        })

    def action_return(self):
        self.is_return = True
