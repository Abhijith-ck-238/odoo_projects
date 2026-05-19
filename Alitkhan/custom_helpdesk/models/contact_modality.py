from odoo import fields, models


class ContractModality(models.Model):
    _inherit = "contract.modality"

    spare_parts_user_ids = fields.Many2many('res.users', string="Spare Parts Responsible",
                                            relation="spare_parts_user_modality_rel",
                                            column1="spare_parts_user_id",
                                            column2="modality_id")
