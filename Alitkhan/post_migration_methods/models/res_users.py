from odoo import models

class ResUsers(models.Model):
    _inherit = "res.users"

    def remove_group_access(self):
        group_user_map = {
            "__export__.cashier": [62, 627, 1159, 58, 616, 762, 1016],
            "account.group_account_invoice": [318, 348, 321, 331, 325, 315, 343, 324, 314, 62, 334, 1106, 1067, 711,
                                              1077, 712, 627, 1159, 1027, 58, 355, 339, 616, 326, 68, 313, 1057, 320,
                                              333, 762, 327, 332, 345, 1016, 1032, 365],
            "account.group_account_user":[62,627,1159,58,616,762,1062],
            "hr.group_hr_user":[1158],
            "sales_team.group_sale_manager":[106, 318, 348, 321, 331, 325, 315, 343, 324, 314, 60, 334,
            1106, 1067, 711, 1077, 712, 112, 1159, 1027, 317, 1158,
            355, 339, 616, 326, 68, 313, 1057, 320, 111, 333, 762,
            1032, 365, 1137, 345, 332, 1161, 327, 628],
            "hr_payroll.group_hr_payroll_manager":[791],
            "purchase.group_purchase_manager": [1157, 1158, 1161],
            "purchase.group_purchase_user": [1158, 1160, 1137, 1161],
            "__export__.res_groups_167_73baca6a": [1159, 1161],
            "contracts.manager_group": [1159, 1161],
            "__export__.res_groups_100_5649fb55": [1159, 1161],
            "contracts.user_group": [1160, 1144, 1137],
            "__export__.res_groups_170_8204bbf3": [1051, 1164, 344, 1031, 113, 1086, 1107, 1179],
            "custom_tech_policies.group_tech_policies_administrator": [1144],
            "custom_product_reservation.group_product_reservation_administrator": [1126],
            "itkan_offering.offering_admin": [1159, 1158, 1161],
            "custom_lower_ks.group_lower_ks_administrator": [35, 773],
            "custom_itkan_project.group_itkan_project_administrator": [39, 1027, 1161, 644, 628],
            "industry_fsm.group_fsm_manager": [106, 111, 762, 1137],
            "custom_industry_fsm.group_fsm_own_ticket_user": [1128, 1171, 60, 1183, 1181, 1182, 1004, 1180, 1046, 333,
                                                              762, 1137, 1172],
            "industry_fsm.group_fsm_user": [106, 1128, 1171, 1174, 790, 1005, 1179, 1132, 1183, 801, 1181, 1182, 1004,
                                            620, 1180, 1156, 1138, 1148, 1164, 712, 1062, 1129, 1096, 1141, 1145, 1034,
                                            1170, 1041, 111, 1135, 762, 1014, 669, 1144, 1151, 1137, 1172, 1161, 723,
                                            115],
            "mrp.group_mrp_manager": [1159, 1160]

        }
        for group_xml_id, user_ids in group_user_map.items():
            group = self.env.ref(group_xml_id, raise_if_not_found=False)
            if not group:
                continue
            users = self.env['res.users'].browse(user_ids)
            group.write({
                'users': [(3, user.id) for user in users]
            })

    def add_group_user(self):
        group_user_map = {
            "industry_fsm.group_fsm_manager": [312,322],
            "industry_fsm.group_fsm_user": [684, 626, 312, 1086, 1103, 654, 1107, 1052, 322, 113,1100, 65, 754, 1045, 1024, 699, 1073, 1085, 1059, 1097, 1066],
            "mrp.group_mrp_manager":[755, 759, 1024, 1097],
            "helpdesk.group_helpdesk_manager":[364, 625, 759],
            "hr_appraisal.group_hr_appraisal_manager":[44, 625, 641, 718, 788],
            "hr_holidays.group_hr_holidays_manager":[44, 53, 63, 625, 688, 718, 759, 788],

        }
        for group_xml_id, user_ids in group_user_map.items():
            group = self.env.ref(group_xml_id, raise_if_not_found=False)
            if not group:
                continue
            users = self.env['res.users'].browse(user_ids)
            group.write({
                'users': [(4, user.id) for user in users]
            })

