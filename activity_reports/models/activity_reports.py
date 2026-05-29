from odoo import models, fields, api

class ActivityReport(models.AbstractModel):
   _name = 'report.activity_reports.report_activity_template'

   @api.model
   def _get_report_values(self, docids, data=None):
       if docids:
           activities = self.env['mail.activity'].browse(docids)
       else:
           activities = self.env['mail.activity'].search([])

       return {
           'doc_ids': docids,
           'doc_model': 'mail.activity',
           'docs': activities,
       }
