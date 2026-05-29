from odoo import models, fields


class CustomProjectTaskType(models.Model):
    _inherit = "project.task.type"

    move_to_stage_limited_users = fields.Many2many("res.users",
                                                   'project_task_type_users_rel',
                                                   column1="type_id",
                                                   column2="user_id",
                                                   string="Limited Users (Responsible for move to this stage)")
    check_product_cart = fields.Boolean(string="Check Product Cart")
    is_the_users_to_be_notified = fields.Boolean(string="Notify Resources")
    out_of_this_stage_alarm_for_modality = fields.Boolean(
        string="Out of this stage alarm for modality")

    out_of_this_stage_alarm_for_resources = fields.Boolean(
        string="Out of this stage alarm for Resources")
    is_not_send_notification = fields.Boolean(string="Not send notification",
                                              help="Disable notification sending "
                                                   "to limited users")
    send_notification_to_spare_parts_responsible = fields.Boolean(string="Send Notification to Spare Parts Responsible")
    confirm_sale_order_if_contract_in_warranty = fields.Boolean(
        string="Confirm Sale Order if Contract in Warranty")
    confirm_sale_order_if_contract_is_expired = fields.Boolean(
        string="Confirm Sale Order if Contract is expired")
