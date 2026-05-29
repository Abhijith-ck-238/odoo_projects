from odoo import models, fields, api, _
from odoo.exceptions import UserError
import datetime


class ResUser(models.Model):
    _inherit="res.users"

    is_free = fields.Boolean(default=True,compute="_compute_is_free")

    def dummy_button(self):
        pass


    def _compute_is_free(self):
        for user in self:
            # print("is_free", user.is_free)
            user.is_free = False
            partner_id = user.partner_id
            calendar_obj = self.env["calendar.event"].search([("partner_ids", "in", partner_id.id)])
            today = fields.Date.context_today(self)

            if not calendar_obj:
                user.is_free=True

            else:
                for item in calendar_obj:
                    if not item.start_date:
                        continue

                    start_date = item.start_date
                    duration = datetime.timedelta(hours=item.duration)

                    end_date = start_date + duration


                    if start_date < today < end_date:
                        user.is_free=False
                        break

                    else:
                        user.is_free=True



