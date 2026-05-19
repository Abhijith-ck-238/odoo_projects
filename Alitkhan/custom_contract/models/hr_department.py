from odoo import models, fields


class CustomHrDepartment(models.Model):
    _inherit = 'hr.department'

    product_show_option = fields.Selection(string='Product Show Option',
                                           selection=[('show_product_char', 'Show Product Char'),
                                                      ('show_product', 'Show Product'), ('show_both', 'Show Both')],
                                           help='Choose product show option',
                                           default="show_product_char"
                                           )
