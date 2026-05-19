from odoo import fields, models, tools


class TrainingReport(models.Model):
    _name = "training.report"
    _description = "Training Analysis Report"
    _auto = False

    training_id = fields.Many2one('training.ticket', 'Training', readonly=True)
    stage_id = fields.Many2one('training.stage', "Stage", readonly=True)
    contract_id = fields.Many2one('contract.contract', "Contract", readonly=True)
    training_type_id = fields.Many2one('training.type', "Training Type", readonly=True)
    analytic_account_id = fields.Many2one('account.analytic.account', "Budget", readonly=True)
    modality_id = fields.Many2one('contract.modality', "Modality", readonly=True)
    partner_id = fields.Many2one('res.partner', "Vendor", readonly=True)
    date = fields.Date("Date")
    training_location_id = fields.Many2one('training.location', "Location", readonly=True)
    site_sector_id = fields.Many2one('site.sector', "Site Sector", readonly=True)
    attendees_count = fields.Integer("Attendees Count", readonly=True)
    attendee_id =fields.Many2one('attendees.attendees', "Attendees")

    def init(self):
        tools.drop_view_if_exists(self.env.cr, "training_report")
        self.env.cr.execute("""CREATE or REPLACE VIEW training_report as (
        SELECT
            min(rl.id) as id,
            rl.id as training_id,
            rl.stage_id as stage_id,
            rl.contract_id as contract_id,
            rl.training_type_id as training_type_id,
            rl.analytic_account_id as analytic_account_id,
            rl.modality_id as modality_id,
            rl.partner_id as partner_id,
            rl.date as date,
            rl.training_location_id as training_location_id,
            rl.site_sector_id as site_sector_id,
            COUNT(r.id) as attendees_count,
            r.attendee_id as attendee_id
        FROM
               training_ticket rl
        JOIN
               training_attendees r on (rl.id=r.training_id)
        GROUP BY
            rl.id,
            rl.stage_id,
            rl.contract_id,
            rl.training_type_id,
            rl.analytic_account_id,
            rl.modality_id,
            rl.partner_id,
            rl.date,
            rl.training_location_id,
            rl.site_sector_id,
            r.attendee_id
        )""")
