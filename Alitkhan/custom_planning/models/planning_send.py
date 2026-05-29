from odoo import models


class CustomPlanningSend(models.TransientModel):
    _inherit = 'planning.send'

    def action_send(self):
        # create the planning
        planning = self.env['planning.planning'].create({
            'start_datetime': self.start_datetime,
            'end_datetime': self.end_datetime,
            'include_unassigned': self.include_unassigned,
            'company_id': self.env.company.id,
        })

        # Get employees to create slots for
        employees = self.employee_ids or self.env['hr.employee'].search([])

        # Create slots manually
        slots = self.env['planning.slot']
        for employee in employees:
            slot_vals = {
                'start_datetime': self.start_datetime,
                'end_datetime': self.end_datetime,
                'employee_id': employee.id,
                'company_id': self.env.company.id,
                'planning_id': planning.id,
            }
            slot = slots.create(slot_vals)

            if employee.user_id:
                note = _("The planning schedule sent.")
                slot.activity_schedule(
                    'custom_planning.mail_activity_send_schedule',
                    note=note,
                    user_id=employee.user_id.id)

        # Send the planning slots
        slots.action_send()
        return {'type': 'ir.actions.act_window_close'}
