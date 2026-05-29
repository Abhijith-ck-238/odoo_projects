from odoo import models, fields


class StockLocation(models.Model):
    _inherit = 'stock.location'

    return_location = fields.Boolean(string='Is a Return Location')
    