from odoo import fields, models


class CrmTeam(models.Model):

    """Inherits the CRM Team model to include a list of follow-up personnel."""
    _inherit = 'crm.team'

    user_ids = fields.Many2many('res.users',
                                string='Followup Personnel',
                                help="Users assigned to follow up on leads and "
                                     "opportunities for this sales team.")
