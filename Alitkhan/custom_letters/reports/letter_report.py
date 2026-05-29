from odoo import fields, models, tools


class LettersReport(models.Model):
    _name = "letter.report"
    _description = "Letters Analysis Report"
    _auto = False

    letter_id = fields.Many2one('letter.ticket', 'Letter', readonly=True)
    stage_id = fields.Many2one('letter.stage', "Stage", readonly=True)
    letter_type_id = fields.Many2one('letter.type', "Letter Type", readonly=True)
    contract_id = fields.Many2one('contract.contract', "Contract", readonly=True)
    modality_id = fields.Many2one('contract.modality', "Modality", readonly=True)
    late_letters = fields.Integer("Late Letters")

    def init(self):
        tools.drop_view_if_exists(self.env.cr, "letter_report")
        self.env.cr.execute("""CREATE or REPLACE VIEW letter_report as (
        SELECT
            min(rl.id) as id,
            rl.id as letter_id,
            rl.stage_id as stage_id,
            rl.letter_type_id as letter_type_id,
            rl.contract_id as contract_id,
            rl.modality_id as modality_id,
            sum(CASE WHEN rl.id in (select res_id from mail_activity where mail_activity.date_deadline < CURRENT_DATE and mail_activity.res_model = 'letter.ticket') THEN 1 ELSE 0 END) as late_letters
        FROM
               letter_ticket rl
        GROUP BY
            rl.id,
            rl.stage_id,
            rl.letter_type_id,
            rl.contract_id,
            rl.modality_id
        )""")
