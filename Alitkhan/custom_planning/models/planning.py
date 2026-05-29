from odoo import models, fields, _
from datetime import timedelta


class PlanningPlanning(models.Model):
    _inherit = 'planning.planning'

    def send_planning(self, message=None):
        """Send planning to employees"""
        self.ensure_one()

        # Get all slots associated with this planning
        slots = self.env['planning.slot'].search([
            ('planning_id', '=', self.id)
        ])

        if slots:
            return slots.action_send()
        return True
