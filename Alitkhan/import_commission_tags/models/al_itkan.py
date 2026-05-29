import xlrd
from odoo import fields, models
import tempfile
import binascii
from odoo.exceptions import UserError
import xlsxwriter
import json




class ImportCommission(models.Model):
    _name = 'al.itkan.model'

    file_to_upload = fields.Binary('File')
    select_value = fields.Selection([('hr_applicant','hr_applicant'),

                                     ('account_move','account_move'),
                                     ('hr_expense','hr_expense'),
                                     ('hr_expense_sheet','hr_expense_sheet'),
                                     ('hr_recruitment_stage','hr_recruitment_stage'),
                                     ('hr_job','hr_job'),
                                     ('product_template','product_template'),
                                     ('hr_employee_public',"hr_employee_public"),
                                     ('calendar_event','calendar_event'),
                                     ('purchase_order','purchase_order'),
                                     ('purchase_order_line','purchase_order_line'),
                                     ('sale_order','sale_order'),
                                     ('sale_order_line','sale_order_line'),
                                     ('stock_quant','stock_quant')
                                     ],String="Model")

    def account_move(self,sheet):
        for row in range(sheet.nrows):

            if row >= 1:
                row_values = sheet.row_values(row)
                object = self.env['account.move'].search([('id', '=', row_values[0])])
                object.company_report_id = row_values[1]

    def hr_expense(self,sheet):
        for row in range(sheet.nrows):

            if row >= 1:
                row_values = sheet.row_values(row)
                object = self.env['hr.expense'].search([('id', '=', row_values[0])])
                if not (row_values[1] == 'False'):
                     object.product_id = row_values[1]
                else:
                    print(row_values[1])

    def hr_expense_sheet(self,sheet):
        for row in range(sheet.nrows):

            if row >= 1:
                row_values = sheet.row_values(row)
                print('row_values[1]',row_values[1])
                if not (row_values[1] == 'False'):

                     sql = 'UPDATE hr_expense_sheet SET analytic_account_id ='+str(row_values[1])+' WHERE id ='+str(row_values[0])
                     if row_values[0] == '7985':
                        print(sql)

                     self.env.cr.execute(sql)

    def hr_recruitment_stage(self,sheet):
        for row in range(sheet.nrows):

            if row >= 1:
                row_values = sheet.row_values(row)
                print('value',row_values)
                object = self.env['hr.recruitment.stage'].search([('id', '=', row_values[0])])
                if not(row_values[1] == 'False'):
                    object.is_interview = row_values[1]
                if not(row_values[2] == 'False'):
                    object.is_accepted = row_values[2]
    def hr_job(self,sheet):
        for row in range(sheet.nrows):

            if row >= 1:
                row_values = sheet.row_values(row)
                object = self.env['hr.job'].search([('id', '=', row_values[0])])
                object.city = row_values[1]
                object.opening_date = row_values[2]
                # object.card_image = row_values[3]
                object.internal_ref = row_values[4]
                if not(row_values[5] == 'False'):
                    object.type_of_position = row_values[5]
                object.technical_knowledge = row_values[6]
                object.behavioral_competencies = row_values[7]
                object.education_language_requirements = row_values[8]
                object.private_job = row_values[9]
                object.notes = row_values[10]
    def product_template(self,sheet):
        for row in range(sheet.nrows):

            if row >= 1:
                row_values = sheet.row_values(row)
                object = self.env['product.template'].search([('id', '=', row_values[0])])
                object.custom_country_of_origin = row_values[1] if not(row_values[1] == 'False') else False
                object.dangerous_goods = row_values[2] if not(row_values[2] == 'False') else False
                object.specifications = row_values[3] if not(row_values[3] == 'False') else False
                object.length = row_values[4] if not(row_values[4] == 'False') else False

    def hr_employee_public(self,sheet):
        for row in range(sheet.nrows):

            if row >= 1:
                row_values = sheet.row_values(row)
                object = self.env['hr.employee.public'].search([('id', '=', row_values[0])])
                object.arabic_name = row_values[1]   if not(row_values[1] == 'False') else False
                object.applicant_id = row_values[2]  if not(row_values[2] == 'False') else False
                object.divisions = row_values[3]  if not(row_values[3] == 'False') else False
                object.units = row_values[4]  if not(row_values[4] == 'False') else False
                object.subunits = row_values[5]  if not(row_values[5] == 'False') else False

    def hr_applicant(self,sheet):
        for row in range(sheet.nrows):

            if row >= 1:
                row_values = sheet.row_values(row)
                # print(row_values[1])
                print(row_values[1] if not(row_values[1] == 'False') else False)
                object = self.env['hr.applicant'].search([('id', '=', row_values[0])])
                object.sudo().write({
                    'surname': row_values[1] if not(row_values[1] == 'False') else False,
                    'arabic_name': row_values[2] if row_values[2] != 'False' else False,
                    'address': row_values[3] if row_values[3] != 'False' else False,
                    'hai': row_values[4] if row_values[4] != 'False' else False,
                    'sec': row_values[5] if row_values[5] != 'False' else False,
                    'st': row_values[6] if row_values[6] != 'False' else False,
                    'house': row_values[7] if row_values[7] != 'False' else False,
                    'nearest': row_values[8] if row_values[8] != 'False' else False,
                    'birthdate': row_values[9] if row_values[9] != 'False' else False,
                    'place_of_birth': row_values[10] if row_values[10] != 'False' else False,
                    'gender': row_values[11] if row_values[11] != 'False' else False,
                    'height': row_values[12] if row_values[12] != 'False' else False,
                    'weight': row_values[13] if row_values[13] != 'False' else False,
                    'citizenship': row_values[14] if row_values[14] != 'False' else False,
                    'religion': row_values[15] if row_values[15] != 'False' else False,
                    'social_status': row_values[16] if row_values[16] != 'False' else False,
                    'father_profession': row_values[17] if row_values[17] != 'False' else False,
                    'mother_profession': row_values[18] if row_values[18] != 'False' else False,
                    'first_name': row_values[19] if row_values[19] != 'False' else False,
                    'profession': row_values[20] if row_values[20] != 'False' else False,
                    'first_name_0': row_values[21] if row_values[21] != 'False' else False,
                    'profession_0': row_values[22] if row_values[22] != 'False' else False,
                    'first_name_1': row_values[23] if row_values[23] != 'False' else False,
                    'profession_1': row_values[24] if row_values[24] != 'False' else False,
                    'first_name_2': row_values[25] if row_values[25] != 'False' else False,
                    'profession_2': row_values[26] if row_values[26] != 'False' else False,
                    'first_name_3': row_values[27] if row_values[27] != 'False' else False,
                    'profession_3': row_values[28] if row_values[28] != 'False' else False,
                    'first_name_4': row_values[29] if row_values[29] != 'False' else False,
                    'profession_4': row_values[30] if row_values[30] != 'False' else False,
                    'first_name_5': row_values[31] if row_values[31] != 'False' else False,
                    'profession_5': row_values[32] if row_values[32] != 'False' else False,
                    'first_name_6': row_values[33] if row_values[33] != 'False' else False,
                    'profession_6': row_values[34] if row_values[34] != 'False' else False,
                    'health_status': row_values[35] if row_values[35] != 'False' else False,
                    'ar_r': row_values[36] if row_values[36] != 'False' else False,
                    'ar_w': row_values[37] if row_values[37] != 'False' else False,
                    'ar_s': row_values[38] if row_values[38] != 'False' else False,
                    'ar_u': row_values[39] if row_values[39] != 'False' else False,
                    'ar_o': row_values[40] if row_values[40] != 'False' else False,
                    'en_r': row_values[41] if row_values[41] != 'False' else False,
                    'en_w': row_values[42] if row_values[42] != 'False' else False,
                    'en_s': row_values[43] if row_values[43] != 'False' else False,
                    'en_u': row_values[44] if row_values[44] != 'False' else False,
                    'en_o': row_values[45] if row_values[45] != 'False' else False,
                    'other_name_0': row_values[46] if row_values[46] != 'False' else False,
                    'other_r_0': row_values[47] if row_values[47] != 'False' else False,
                    'other_w_0': row_values[48] if row_values[48] != 'False' else False,
                    'other_s_0': row_values[49] if row_values[49] != 'False' else False,
                    'other_u_0': row_values[50] if row_values[50] != 'False' else False,
                    'other_o_0': row_values[51] if row_values[51] != 'False' else False,
                    'other_name_1': row_values[52] if row_values[52] != 'False' else False,
                    'other_r_1': row_values[53] if row_values[53] != 'False' else False,
                    'other_w_1': row_values[54] if row_values[54] != 'False' else False,
                    'other_s_1': row_values[55] if row_values[55] != 'False' else False,
                    'other_u_1': row_values[56] if row_values[56] != 'False' else False,
                    'other_o_1': row_values[57] if row_values[57] != 'False' else False,
                    'primary_name': row_values[58] if row_values[58] != 'False' else False,
                    'primary_years': row_values[59] if row_values[59] != 'False' else False,
                    'primary_avg': row_values[60] if row_values[60] != 'False' else False,
                    'Intermediate_name': row_values[61] if row_values[61] != 'False' else False,
                    'Intermediate_years': row_values[62] if row_values[62] != 'False' else False,
                    'Intermediate_avg': row_values[63] if row_values[63] != 'False' else False,
                    'secondary_name': row_values[64] if row_values[64] != 'False' else False,
                    'secondary_years': row_values[65] if row_values[65] != 'False' else False,
                    'secondary_avg': row_values[66] if row_values[66] != 'False' else False,
                    'college_name': row_values[67] if row_values[67] != 'False' else False,
                    'college_major': row_values[68] if row_values[68] != 'False' else False,
                    'college_years': row_values[69] if row_values[69] != 'False' else False,
                    'college_avg': row_values[70] if row_values[70] != 'False' else False,
                    'other_0_name': row_values[71] if row_values[71] != 'False' else False,
                    'other_0_years': row_values[72] if row_values[72] != 'False' else False,
                    'other_0_avg': row_values[73] if row_values[73] != 'False' else False,
                    'other_1_name': row_values[74] if row_values[74] != 'False' else False,
                    'other_1_years': row_values[75] if row_values[75] != 'False' else False,
                    'other_1_avg': row_values[76] if row_values[76] != 'False' else False,
                    'highest_acad': row_values[77] if row_values[77] != 'False' else False,
                    'major': row_values[78] if row_values[78] != 'False' else False,
                    'highest_grad_year': row_values[79] if row_values[79] != 'False' else False,
                    'highest_uni': row_values[80] if row_values[80] != 'False' else False,
                    'highest_country': row_values[81] if row_values[81] != 'False' else False,
                    'referral_source': row_values[82] if row_values[82] != 'False' else False,
                    'other_referral_source': row_values[83] if row_values[83] != 'False' else False,
                    'preffered_fow': row_values[84] if row_values[84] != 'False' else False,
                    'skill_0_Desc': row_values[85] if row_values[85] != 'False' else False,
                    'skill_0_level': row_values[86] if row_values[86] != 'False' else False,
                    'skill_1_Desc': row_values[87] if row_values[87] != 'False' else False,
                    'skill_1_level': row_values[88] if row_values[88] != 'False' else False,
                    'skill_2_Desc': row_values[89] if row_values[89] != 'False' else False,
                    'skill_2_level': row_values[90] if row_values[90] != 'False' else False,
                    'skill_3_Desc': row_values[91] if row_values[91] != 'False' else False,
                    'skill_3_level': row_values[92] if row_values[92] != 'False' else False,
                    'skill_4_Desc': row_values[93] if row_values[93] != 'False' else False,
                    'skill_4_level': row_values[94] if row_values[94] != 'False' else False,
                    'skill_5_Desc': row_values[95] if row_values[95] != 'False' else False,
                    'skill_5_level': row_values[96] if row_values[96] != 'False' else False,
                    'business_correspondence_skill_level': row_values[97] if row_values[97] != 'False' else False,
                    'effective_communication_skill_level': row_values[98] if row_values[98] != 'False' else False,
                    'customer_service_skill_level': row_values[99] if row_values[99] != 'False' else False,
                    'team_work_skill_level': row_values[100] if row_values[100] != 'False' else False,
                    'Internet_and_research_skill_level': row_values[101] if row_values[101] != 'False' else False,
                    'ms_office_and_outlook_skill_level': row_values[102] if row_values[102] != 'False' else False,
                    'office_machine_skill_level': row_values[103] if row_values[103] != 'False' else False,
                    'typing_skill_level': row_values[104] if row_values[104] != 'False' else False,
                    'time_management_skill_level': row_values[105] if row_values[105] != 'False' else False,
                    'attention_to_detail_level': row_values[106] if row_values[106] != 'False' else False,
                    'goal_oriented_skill_level': row_values[107] if row_values[107] != 'False' else False,
                    'multi_tasking_skill_level': row_values[108] if row_values[108] != 'False' else False,
                    'follow_up_skill_level': row_values[109] if row_values[109] != 'False' else False,
                    'employee_relation_skill_level': row_values[110] if row_values[110] != 'False' else False,
                    'supervision_skill_level': row_values[111] if row_values[111] != 'False' else False,
                    'relationship_building_skill_level': row_values[112] if row_values[112] != 'False' else False,
                    'time_management_skill_level': row_values[113] if row_values[113] != 'False' else False,
                    'research_information_gathering_skill_level': row_values[114] if row_values[114] != 'False' else False,
                    'medical_product_knowledge_skill_level': row_values[115] if row_values[115] != 'False' else False,
                    'business_communication_skill_level': row_values[116] if row_values[116] != 'False' else False,
                    'client_engagement_skill_level': row_values[117] if row_values[117] != 'False' else False,
                    'sales_presentations_demos_skill_level': row_values[118] if row_values[118] != 'False' else False,
                    'contract_negotiation_skill_level': row_values[119] if row_values[119] != 'False' else False,
                    'closing_skills_skill_level': row_values[120] if row_values[120] != 'False' else False,
                    'self_motivated_ambitious_skill_level': row_values[121] if row_values[121] != 'False' else False,
                    'adaptability_skill_level': row_values[122] if row_values[122] != 'False' else False,
                    'responsibility_skill_level': row_values[123] if row_values[123] != 'False' else False,
                    'goal_oriented_skill_level': row_values[124] if row_values[124] != 'False' else False,
                    'passionate_about_selling_skill_level': row_values[125] if row_values[125] != 'False' else False,
                    't0': row_values[126] if row_values[126] != 'False' else False,
                    't0_year': row_values[127] if row_values[127] != 'False' else False,
                    't0_awarded_by': row_values[128] if row_values[128] != 'False' else False,
                    't0_country_city': row_values[129] if row_values[129] != 'False' else False,
                    't1': row_values[130] if row_values[130] != 'False' else False,
                    't1_year': row_values[131] if row_values[131] != 'False' else False,
                    't1_awarded_by': row_values[132] if row_values[132] != 'False' else False,
                    't1_country_city': row_values[133] if row_values[133] != 'False' else False,
                    't2': row_values[134] if row_values[134] != 'False' else False,
                    't2_year': row_values[135] if row_values[135] != 'False' else False,
                    't2_awarded_by': row_values[136] if row_values[136] != 'False' else False,
                    't2_country_city': row_values[137] if row_values[137] != 'False' else False,
                    't3': row_values[138] if row_values[138] != 'False' else False,
                    't3_year': row_values[139] if row_values[139] != 'False' else False,
                    't3_awarded_by': row_values[140] if row_values[140] != 'False' else False,
                    't3_country_city': row_values[141] if row_values[141] != 'False' else False,
                    't4': row_values[142] if row_values[142] != 'False' else False,
                    't4_year': row_values[143] if row_values[143] != 'False' else False,
                    't4_awarded_by': row_values[144] if row_values[144] != 'False' else False,
                    't4_country_city': row_values[145] if row_values[145] != 'False' else False,
                    't5': row_values[146] if row_values[146] != 'False' else False,
                    't5_year': row_values[147] if row_values[147] != 'False' else False,
                    't5_awarded_by': row_values[148] if row_values[148] != 'False' else False,
                    't5_country_city': row_values[149] if row_values[149] != 'False' else False,
                    'contact_disclaimer': row_values[150] if row_values[150] != 'False' else False,
                    'employer_name': row_values[151] if row_values[151] != 'False' else False,
                    'job_title': row_values[152] if row_values[152] != 'False' else False,
                    'employer_address': row_values[153] if row_values[153] != 'False' else False,
                    'employer_province': row_values[154] if row_values[154] != 'False' else False,
                    'from_date': row_values[155] if row_values[155] != 'False' else False,
                    'to_date': row_values[156] if row_values[156] != 'False' else False,
                    'starting_slry': row_values[157] if row_values[157] != 'False' else False,
                    'ending_slry': row_values[158] if row_values[158] != 'False' else False,
                    'supervisor': row_values[159] if row_values[159] != 'False' else False,
                    'super_phone': row_values[160] if row_values[160] != 'False' else False,
                    'reason_for_leaving': row_values[161] if row_values[161] != 'False' else False,
                    'employer_name_0': row_values[162] if row_values[162] != 'False' else False,
                    'job_title_0': row_values[163] if row_values[163] != 'False' else False,
                    'employer_address_0': row_values[164] if row_values[164] != 'False' else False,
                    'employer_province_0': row_values[165] if row_values[165] != 'False' else False,
                    'from_date_0': row_values[166] if row_values[166] != 'False' else False,
                    'to_date_0': row_values[167] if row_values[167] != 'False' else False,
                    'starting_slry_0': row_values[168] if row_values[168] != 'False' else False,
                    'ending_slry_0': row_values[169] if row_values[169] != 'False' else False,
                    'supervisor_0': row_values[170] if row_values[170] != 'False' else False,
                    'super_phone_0': row_values[171] if row_values[171] != 'False' else False,
                    'reason_for_leaving_0': row_values[172] if row_values[172] != 'False' else False,
                    'employer_name_1': row_values[173] if row_values[173] != 'False' else False,
                    'job_title_1': row_values[174] if row_values[174] != 'False' else False,
                    'employer_address_1': row_values[175] if row_values[175] != 'False' else False,
                    'employer_province_1': row_values[176] if row_values[176] != 'False' else False,
                    'from_date_1': row_values[177] if row_values[177] != 'False' else False,
                    'to_date_1': row_values[178] if row_values[178] != 'False' else False,
                    'starting_slry_1': row_values[179] if row_values[179] != 'False' else False,
                    'ending_slry_1': row_values[180] if row_values[180] != 'False' else False,
                    'supervisor_1': row_values[181] if row_values[181] != 'False' else False,
                    'super_phone_1': row_values[182] if row_values[182] != 'False' else False,
                    'reason_for_leaving_1': row_values[183] if row_values[183] != 'False' else False,
                    'union_member': row_values[184] if row_values[184] != 'False' else False,
                    'union_member_date': row_values[185] if row_values[185] != 'False' else False,
                    'driver_license': row_values[186] if row_values[186] != 'False' else False,
                    'driver_license_date': row_values[187] if row_values[187] != 'False' else False,
                    'means_of_transport': row_values[188] if row_values[188] != 'False' else False,
                    'good_appoint': row_values[189] if row_values[189] != 'False' else False,
                    'smoking': row_values[190] if row_values[190] != 'False' else False,
                    'long_hours': row_values[191] if row_values[191] != 'False' else False,
                    'start_date': row_values[192] if row_values[192] != 'False' else False,
                    'planning_to_study': row_values[193] if row_values[193] != 'False' else False,
                    'presently_employed': row_values[194] if row_values[194] != 'False' else False,
                    'contact_employer': row_values[195] if row_values[195] != 'False' else False,
                    'team_work': row_values[196] if row_values[196] != 'False' else False,
                    'pressure': row_values[197] if row_values[197] != 'False' else False,
                    'travel': row_values[198] if row_values[198] != 'False' else False,
                    'ref_name': row_values[199] if row_values[199] != 'False' else False,
                    'ref_relation': row_values[200] if row_values[200] != 'False' else False,
                    'ref_phone': row_values[201] if row_values[201] != 'False' else False,
                    'ref_name_1': row_values[202] if row_values[202] != 'False' else False,
                    'ref_relation_1': row_values[203] if row_values[203] != 'False' else False,
                    'ref_phone_1': row_values[204] if row_values[204] != 'False' else False,
                    'ref_r_name': row_values[205] if row_values[205] != 'False' else False,
                    'ref_r_relation': row_values[206] if row_values[206] != 'False' else False,
                    'ref_r_phone': row_values[207] if row_values[207] != 'False' else False,
                    'ref_r_name_1': row_values[208] if row_values[208] != 'False' else False,
                    'ref_r_relation_1': row_values[209] if row_values[209] != 'False' else False,
                    # 'ref_r_phone_1': row_values[210] if row_values[210] != 'False' else False,
                    'signature': row_values[211] if row_values[211] != 'False' else False,
                    'sig_date': row_values[212] if row_values[212] != 'False' else False,
                    'skype_id': row_values[223] if row_values[223] != 'False' else False,
                    'external_ref': row_values[224] if row_values[224] != 'False' else False,
                })

    def calendar_event(self,sheet):
        print("calender")
        for row in range(sheet.nrows):

            if row >= 1:
                row_values = sheet.row_values(row)
                print(row_values)
                object = self.env['calendar.event'].search([('id', '=', row_values[0])])

                # object.send_email_to_attendees = False if row_values[1] == 'False' else True
                object.send_email_to_attendees= False if row_values[1] == 'False'  else True
                # # sql = 'UPDATE calendar_event SET send_email_to_attendees =' + str(row_values[1]) + ' WHERE id =' + str(row_values[0])
                # self.env.cr.execute(sql)

    def purchase_order(self,sheet):
        print("purchase order")
        for row in range(sheet.nrows):

            if row >= 1:
                row_values = sheet.row_values(row)
                object = self.env['purchase.order'].search([('id', '=', row_values[0])])
                object.sent_prouduct_info = row_values[1]

    def purchase_order_line(self,sheet):
        print("yes")
        for row in range(sheet.nrows):

            if row >= 1:
                row_values = sheet.row_values(row)
                object = self.env['purchase.order.line'].search([('id', '=', row_values[0])])
                object.product_smn = False if row_values[1] == 'False'  else row_values[1]
                object.serial_number =  False if row_values[2] == 'False'  else row_values[2]
                object.customer_id = False if row_values[3] == 'False'  else row_values[3]
                object.brand_id =  False if row_values[4] == 'False'  else row_values[4]

    def sale_order(self, sheet):
        print("yes")
        for row in range(sheet.nrows):

            if row >= 1:
                row_values = sheet.row_values(row)
                object = self.env['sale.order'].search([('id', '=', row_values[0])])
                object.date_order = False if row_values[1] == 'False' else row_values[1]
                object.company_report_id = False if row_values[2] == 'False' else row_values[2]

    def sale_order_line(self,sheet):
        for row in range(sheet.nrows):

            if row >= 1:
                row_values = sheet.row_values(row)
                object = self.env['sale.order'].search([('id', '=', row_values[0])])
                object.product_smn = False if row_values[1] == 'False' else row_values[1]

    def stock_quant(self,sheet):
        for row in range(sheet.nrows):

            if row >= 1:
                row_values = sheet.row_values(row)
                object = self.env['stock.quant'].search([('id', '=', row_values[0])])
                object.lot_expire_date = False if row_values[1] == 'False' else row_values[1]


    def action_custom_expense_models(self):
        print("sdd")
        fp = tempfile.NamedTemporaryFile(delete=False, suffix=".xlsx")
        fp.write(binascii.a2b_base64(self.file_to_upload))
        fp.seek(0)
        values = {}
        workbook = xlrd.open_workbook(fp.name)
        sheet = workbook.sheet_by_index(0)
        lines = []
        if self.select_value =='hr_applicant':
            self.hr_applicant(sheet)
        if self.select_value == 'account_move':
            self.account_move(sheet)
        if self.select_value == 'hr_expense':
            self.hr_expense(sheet)
        if self.select_value == 'hr_expense_sheet':
            self.hr_expense_sheet(sheet)
        if self.select_value == 'hr_recruitment_stage':
            self.hr_recruitment_stage(sheet)
        if self.select_value == 'hr_job':
            self.hr_job(sheet)
        if self.select_value == 'product_template':
            self.product_template(sheet)
        if self.select_value == 'hr_employee_public':
            self.hr_employee_public(sheet)
        if self.select_value == 'calendar_event':
            self.calendar_event(sheet)
        if self.select_value == 'purchase_order':
            self.purchase_order(sheet)
        if self.select_value == 'purchase_order_line':
            self.purchase_order_line(sheet)
        if self.select_value == 'sale_order':
            self.sale_order(sheet)
        if self.select_value =='sale_order_line':
            self.sale_order_line(sheet)
        if self.select_value == 'stock_quant':
            self.stock_quant(sheet)


    def cron_al_itkan_models(self):
        self.ensure_one()

        temp=self.env["hr.applicant"].search([])
        workbook = xlsxwriter.Workbook('/home/cybrosys/Videos/al_itkan/hr_applicant.xlsx')
        worksheet = workbook.add_worksheet()
        row=-1
        for rec in temp:
            row=row+1
            worksheet.write(row,0,str(rec.id))
            for i in rec:
                worksheet.write(row, 1, str(i.surname))
            for i in rec:
                worksheet.write(row, 2, str(i.arabic_name))
            for i in rec:
                worksheet.write(row, 3, str(i.address))
            for i in rec:
                worksheet.write(row, 4, str(i.hai))
            for i in rec:
                worksheet.write(row, 5, str(i.sec))
            for i in rec:
                worksheet.write(row, 6, str(i.st))
            for i in rec:
                worksheet.write(row, 7, str(i.house))
            for i in rec:
                worksheet.write(row, 8, str(i.nearest))
            for i in rec:
                worksheet.write(row, 9, str(i.birthdate))
            for i in rec:
                worksheet.write(row, 10, str(i.place_of_birth))
            for i in rec:
                worksheet.write(row, 11, str(i.gender))
            for i in rec:
                worksheet.write(row, 12, str(i.height))
            for i in rec:
                worksheet.write(row, 13, str(i.weight))
            for i in rec:
                worksheet.write(row, 14, str(i.citizenship))
            for i in rec:
                worksheet.write(row, 15, str(i.religion))
            for i in rec:
                worksheet.write(row, 16, str(i.social_status))
            for i in rec:
                worksheet.write(row, 17, str(i.father_profession))
            for i in rec:
                worksheet.write(row, 18, str(i.mother_profession))
            for i in rec:
                worksheet.write(row, 19, str(i.first_name))
            for i in rec:
                worksheet.write(row, 20, str(i.profession))
            for i in rec:
                worksheet.write(row, 21, str(i.first_name_0))
            for i in rec:
                worksheet.write(row, 22, str(i.profession_0))
            for i in rec:
                worksheet.write(row, 23, str(i.first_name_1))
            for i in rec:
                worksheet.write(row, 24, str(i.profession_1))
            for i in rec:
                worksheet.write(row, 25, str(i.first_name_2))
            for i in rec:
                worksheet.write(row, 26, str(i.profession_2))
            for i in rec:
                worksheet.write(row, 27, str(i.first_name_3))
            for i in rec:
                worksheet.write(row, 28, str(i.profession_3))
            for i in rec:
                worksheet.write(row, 29, str(i.first_name_4))
            for i in rec:
                worksheet.write(row, 30, str(i.profession_4))
            for i in rec:
                worksheet.write(row, 31, str(i.first_name_5))
            for i in rec:
                worksheet.write(row, 32, str(i.profession_5))
            for i in rec:
                worksheet.write(row, 33, str(i.first_name_6))
            for i in rec:
                worksheet.write(row, 34, str(i.profession_6))
            for i in rec:
                worksheet.write(row, 35, str(i.health_status))
            for i in rec:
                worksheet.write(row, 36, str(i.ar_r))
            for i in rec:
                worksheet.write(row, 37, str(i.ar_w))
            for i in rec:
                worksheet.write(row, 38, str(i.ar_s))
            for i in rec:
                worksheet.write(row, 39, str(i.ar_u))
            for i in rec:
                worksheet.write(row, 40, str(i.ar_o))
            for i in rec:
                worksheet.write(row, 41, str(i.en_r))
            for i in rec:
                worksheet.write(row, 42, str(i.en_w))
            for i in rec:
                worksheet.write(row, 43, str(i.en_s))
            for i in rec:
                worksheet.write(row, 44, str(i.en_u))
            for i in rec:
                worksheet.write(row, 45, str(i.en_o))
            for i in rec:
                worksheet.write(row, 46, str(i.other_name_0))
            for i in rec:
                worksheet.write(row, 47, str(i.other_r_0))
            for i in rec:
                worksheet.write(row, 48, str(i.other_w_0))
            for i in rec:
                worksheet.write(row, 49, str(i.other_s_0))
            for i in rec:
                worksheet.write(row, 50, str(i.other_u_0))
            for i in rec:
                worksheet.write(row, 51, str(i.other_o_0))
            for i in rec:
                worksheet.write(row, 52, str(i.other_name_1))
            for i in rec:
                worksheet.write(row, 53, str(i.other_r_1))
            for i in rec:
                worksheet.write(row, 54, str(i.other_w_1))
            for i in rec:
                worksheet.write(row, 55, str(i.other_s_1))
            for i in rec:
                worksheet.write(row, 56, str(i.other_u_1))
            for i in rec:
                worksheet.write(row, 57, str(i.other_o_1))
            for i in rec:
                worksheet.write(row, 58, str(i.primary_name))
            for i in rec:
                worksheet.write(row, 59, str(i.primary_years))
            for i in rec:
                worksheet.write(row, 60, str(i.primary_avg))
            for i in rec:
                worksheet.write(row, 61, str(i.Intermediate_name))
            for i in rec:
                worksheet.write(row, 62, str(i.Intermediate_years))
            for i in rec:
                worksheet.write(row, 63, str(i.Intermediate_avg))
            for i in rec:
                worksheet.write(row, 64, str(i.secondary_name))
            for i in rec:
                worksheet.write(row, 65, str(i.secondary_years))
            for i in rec:
                worksheet.write(row, 66, str(i.secondary_avg))
            for i in rec:
                worksheet.write(row, 67, str(i.college_name))
            for i in rec:
                worksheet.write(row, 68, str(i.college_major))
            for i in rec:
                worksheet.write(row, 69, str(i.college_years))
            for i in rec:
                worksheet.write(row, 70, str(i.college_avg))
            for i in rec:
                worksheet.write(row, 71, str(i.other_0_name))
            for i in rec:
                worksheet.write(row, 72, str(i.other_0_years))
            for i in rec:
                worksheet.write(row, 73, str(i.other_0_avg))
            for i in rec:
                worksheet.write(row, 74, str(i.other_1_name))
            for i in rec:
                worksheet.write(row, 75, str(i.other_1_years))
            for i in rec:
                worksheet.write(row, 76, str(i.other_1_avg))
            for i in rec:
                worksheet.write(row, 77, str(i.highest_acad))
            for i in rec:
                worksheet.write(row, 78, str(i.major))
            for i in rec:
                worksheet.write(row, 79, str(i.highest_grad_year))
            for i in rec:
                worksheet.write(row, 80, str(i.highest_uni))
            for i in rec:
                worksheet.write(row, 81, str(i.highest_country))
            for i in rec:
                worksheet.write(row, 82, str(i.referral_source))
            for i in rec:
                worksheet.write(row, 83, str(i.other_referral_source))
            for i in rec:
                worksheet.write(row, 84, str(i.preffered_fow))
            for i in rec:
                worksheet.write(row, 85, str(i.skill_0_Desc))
            for i in rec:
                worksheet.write(row, 86, str(i.skill_0_level))
            for i in rec:
                worksheet.write(row, 87, str(i.skill_1_Desc))
            for i in rec:
                worksheet.write(row, 88, str(i.skill_1_level))
            for i in rec:
                worksheet.write(row, 89, str(i.skill_2_Desc))
            for i in rec:
                worksheet.write(row, 90, str(i.skill_2_level))
            for i in rec:
                worksheet.write(row, 91, str(i.skill_3_Desc))
            for i in rec:
                worksheet.write(row, 92, str(i.skill_3_level))
            for i in rec:
                worksheet.write(row, 93, str(i.skill_4_Desc))
            for i in rec:
                worksheet.write(row, 94, str(i.skill_4_level))
            for i in rec:
                worksheet.write(row, 95, str(i.skill_5_Desc))
            for i in rec:
                worksheet.write(row, 96, str(i.skill_5_level))
            for i in rec:
                worksheet.write(row, 97, str(i.business_correspondence_skill_level))
            for i in rec:
                worksheet.write(row, 98, str(i.effective_communication_skill_level))
            for i in rec:
                worksheet.write(row, 99, str(i.customer_service_skill_level))
            for i in rec:
                worksheet.write(row, 100, str(i.team_work_skill_level))
            for i in rec:
                worksheet.write(row, 101, str(i.Internet_and_research_skill_level))
            for i in rec:
                worksheet.write(row, 102, str(i.ms_office_and_outlook_skill_level))
            for i in rec:
                worksheet.write(row, 103, str(i.office_machine_skill_level))
            for i in rec:
                worksheet.write(row, 104, str(i.typing_skill_level))
            for i in rec:
                worksheet.write(row, 105, str(i.time_management_skill_level))
            for i in rec:
                worksheet.write(row, 106, str(i.attention_to_detail_level))
            for i in rec:
                worksheet.write(row, 107, str(i.goal_oriented_skill_level))
            for i in rec:
                worksheet.write(row, 108, str(i.multi_tasking_skill_level))
            for i in rec:
                worksheet.write(row, 109, str(i.follow_up_skill_level))
            for i in rec:
                worksheet.write(row, 110, str(i.employee_relation_skill_level))
            for i in rec:
                worksheet.write(row, 111, str(i.supervision_skill_level))
            for i in rec:
                worksheet.write(row, 112, str(i.relationship_building_skill_level))
            for i in rec:
                worksheet.write(row, 113, str(i.time_management_skill_level))
            for i in rec:
                worksheet.write(row, 114, str(i.research_information_gathering_skill_level))
            for i in rec:
                worksheet.write(row, 115, str(i.medical_product_knowledge_skill_level))
            for i in rec:
                worksheet.write(row, 116, str(i.business_communication_skill_level))
            for i in rec:
                worksheet.write(row, 117, str(i.client_engagement_skill_level))
            for i in rec:
                worksheet.write(row, 118, str(i.sales_presentations_demos_skill_level))
            for i in rec:
                worksheet.write(row, 119, str(i.contract_negotiation_skill_level))
            for i in rec:
                worksheet.write(row, 120, str(i.closing_skills_skill_level))
            for i in rec:
                worksheet.write(row, 121, str(i.self_motivated_ambitious_skill_level))
            for i in rec:
                worksheet.write(row, 122, str(i.adaptability_skill_level))
            for i in rec:
                worksheet.write(row, 123, str(i.responsibility_skill_level))
            for i in rec:
                worksheet.write(row, 124, str(i.goal_oriented_skill_level))
            for i in rec:
                worksheet.write(row, 125, str(i.passionate_about_selling_skill_level))
            for i in rec:
                worksheet.write(row, 126, str(i.t0))
            for i in rec:
                worksheet.write(row, 127, str(i.t0_year))
            for i in rec:
                worksheet.write(row, 128, str(i.t0_awarded_by))
            for i in rec:
                worksheet.write(row, 129, str(i.t0_country_city))
            for i in rec:
                worksheet.write(row, 130, str(i.t1))
            for i in rec:
                worksheet.write(row, 131, str(i.t1_year))
            for i in rec:
                worksheet.write(row, 132, str(i.t1_awarded_by))
            for i in rec:
                worksheet.write(row, 133, str(i.t1_country_city))
            for i in rec:
                worksheet.write(row, 134, str(i.t2))
            for i in rec:
                worksheet.write(row, 135, str(i.t2_year))
            for i in rec:
                worksheet.write(row, 136, str(i.t2_awarded_by))
            for i in rec:
                worksheet.write(row, 137, str(i.t2_country_city))
            for i in rec:
                worksheet.write(row, 138, str(i.t3))
            for i in rec:
                worksheet.write(row, 139, str(i.t3_year))
            for i in rec:
                worksheet.write(row, 140, str(i.t3_awarded_by))
            for i in rec:
                worksheet.write(row, 141, str(i.t3_country_city))
            for i in rec:
                worksheet.write(row, 142, str(i.t4))
            for i in rec:
                worksheet.write(row, 143, str(i.t4_year))
            for i in rec:
                worksheet.write(row, 144, str(i.t4_awarded_by))
            for i in rec:
                worksheet.write(row, 145, str(i.t4_country_city))
            for i in rec:
                worksheet.write(row, 146, str(i.t5))
            for i in rec:
                worksheet.write(row, 147, str(i.t5_year))
            for i in rec:
                worksheet.write(row, 148, str(i.t5_awarded_by))
            for i in rec:
                worksheet.write(row, 149, str(i.t5_country_city))
            for i in rec:
                worksheet.write(row, 150, str(i.contact_disclaimer))
            for i in rec:
                worksheet.write(row, 151, str(i.employer_name))
            for i in rec:
                worksheet.write(row, 152, str(i.job_title))
            for i in rec:
                worksheet.write(row, 153, str(i.employer_address))
            for i in rec:
                worksheet.write(row, 154, str(i.employer_province))
            for i in rec:
                worksheet.write(row, 155, str(i.from_date))
            for i in rec:
                worksheet.write(row, 156, str(i.to_date))
            for i in rec:
                worksheet.write(row, 157, str(i.starting_slry))
            for i in rec:
                worksheet.write(row, 158, str(i.ending_slry))
            for i in rec:
                worksheet.write(row, 159, str(i.supervisor))
            for i in rec:
                worksheet.write(row, 160, str(i.super_phone))
            for i in rec:
                worksheet.write(row, 161, str(i.reason_for_leaving))
            for i in rec:
                worksheet.write(row, 162, str(i.employer_name_0))
            for i in rec:
                worksheet.write(row, 163, str(i.job_title_0))
            for i in rec:
                worksheet.write(row, 164, str(i.employer_address_0))
            for i in rec:
                worksheet.write(row, 165, str(i.employer_province_0))
            for i in rec:
                worksheet.write(row, 166, str(i.from_date_0))
            for i in rec:
                worksheet.write(row, 167, str(i.to_date_0))
            for i in rec:
                worksheet.write(row, 168, str(i.starting_slry_0))
            for i in rec:
                worksheet.write(row, 169, str(i.ending_slry_0))
            for i in rec:
                worksheet.write(row, 170, str(i.supervisor_0))
            for i in rec:
                worksheet.write(row, 171, str(i.super_phone_0))
            for i in rec:
                worksheet.write(row, 172, str(i.reason_for_leaving_0))
            for i in rec:
                worksheet.write(row, 173, str(i.employer_name_1))
            for i in rec:
                worksheet.write(row, 174, str(i.job_title_1))
            for i in rec:
                worksheet.write(row, 175, str(i.employer_address_1))
            for i in rec:
                worksheet.write(row, 176, str(i.employer_province_1))
            for i in rec:
                worksheet.write(row, 177, str(i.from_date_1))
            for i in rec:
                worksheet.write(row, 178, str(i.to_date_1))
            for i in rec:
                worksheet.write(row, 179, str(i.starting_slry_1))
            for i in rec:
                worksheet.write(row, 180, str(i.ending_slry_1))
            for i in rec:
                worksheet.write(row, 181, str(i.supervisor_1))
            for i in rec:
                worksheet.write(row, 182, str(i.super_phone_1))
            for i in rec:
                worksheet.write(row, 183, str(i.reason_for_leaving_1))
            for i in rec:
                worksheet.write(row, 184, str(i.union_member))
            for i in rec:
                worksheet.write(row, 185, str(i.union_member_date))
            for i in rec:
                worksheet.write(row, 186, str(i.driver_license))
            for i in rec:
                worksheet.write(row, 187, str(i.driver_license_date))
            for i in rec:
                worksheet.write(row, 188, str(i.means_of_transport))
            for i in rec:
                worksheet.write(row, 189, str(i.good_appoint))
            for i in rec:
                worksheet.write(row, 190, str(i.smoking))
            for i in rec:
                worksheet.write(row, 191, str(i.long_hours))
            for i in rec:
                worksheet.write(row, 192, str(i.start_date))
            for i in rec:
                worksheet.write(row, 193, str(i.planning_to_study))
            for i in rec:
                worksheet.write(row, 194, str(i.presently_employed))
            for i in rec:
                worksheet.write(row, 195, str(i.contact_employer))
            for i in rec:
                worksheet.write(row, 196, str(i.team_work))
            for i in rec:
                worksheet.write(row, 197, str(i.pressure))
            for i in rec:
                worksheet.write(row, 198, str(i.travel))
            for i in rec:
                worksheet.write(row, 199, str(i.ref_name))
            for i in rec:
                worksheet.write(row, 200, str(i.ref_relation))
            for i in rec:
                worksheet.write(row, 201, str(i.ref_phone))
            for i in rec:
                worksheet.write(row, 202, str(i.ref_name_1))
            for i in rec:
                worksheet.write(row, 203, str(i.ref_relation_1))
            for i in rec:
                worksheet.write(row, 204, str(i.ref_phone_1))
            for i in rec:
                worksheet.write(row, 205, str(i.ref_r_name))
            for i in rec:
                worksheet.write(row, 206, str(i.ref_r_relation))
            for i in rec:
                worksheet.write(row, 207, str(i.ref_r_phone))
            for i in rec:
                worksheet.write(row, 208, str(i.ref_r_name_1))
            for i in rec:
                worksheet.write(row, 209, str(i.ref_r_relation_1))
            for i in rec:
                worksheet.write(row, 210, str(i.ref_r_phone_1))
            for i in rec:
                worksheet.write(row, 211, str(i.signature))
            for i in rec:
                worksheet.write(row, 212, str(i.sig_date))
            for i in rec:
                worksheet.write(row, 213, str(i.photo))
            for i in rec:
                worksheet.write(row, 214, str(i.national_id))
            for i in rec:
                worksheet.write(row, 215, str(i.citizenship_cert))
            for i in rec:
                worksheet.write(row, 216, str(i.accomodation_id))
            for i in rec:
                worksheet.write(row, 217, str(i.uni_degree))
            for i in rec:
                worksheet.write(row, 218, str(i.medical))
            for i in rec:
                worksheet.write(row, 219, str(i.no_crim_req))
            for i in rec:
                worksheet.write(row, 220, str(i.letter_rec_1))
            for i in rec:
                worksheet.write(row, 221, str(i.letter_rec_2))
            for i in rec:
                worksheet.write(row, 222, str(i.cv))
            for i in rec:
                worksheet.write(row, 223, str(i.skype_id))
            for i in rec:
                worksheet.write(row, 224, str(i.external_ref))


        workbook.close()
        temp = self.env['account.move'].search([])
        workbook = xlsxwriter.Workbook('/home/cybrosys/Videos/al_itkan/account_move.xlsx')
        worksheet = workbook.add_worksheet()
        row = -1
        for i in temp:
            row =row + 1
            worksheet.write(row,0 , str(i.id))
            worksheet.write(row, 1, str(i.company_report_id.id))
        workbook.close()
        temp = self.env['hr.expense'].search([])
        workbook = xlsxwriter.Workbook('/home/cybrosys/Videos/al_itkan/hr_expense.xlsx')
        worksheet = workbook.add_worksheet()
        row = -1
        for i in temp:
            row = row+1
            worksheet.write(row, 0, str(i.id))
            worksheet.write(row, 1, str(i.product_id.id))
        workbook.close()
        temp = self.env['hr.expense.sheet'].search([])
        workbook = xlsxwriter.Workbook('/home/cybrosys/Videos/al_itkan/hr_expense_sheet.xlsx')
        worksheet = workbook.add_worksheet()
        row = -1
        for i in temp:
            row = row + 1
            worksheet.write(row,0,str(i.id))
            worksheet.write(row, 1, str(i.analytic_account_id.id))
        workbook.close()
        temp = self.env['hr.recruitment.stage'].search([])
        workbook = xlsxwriter.Workbook('/home/cybrosys/Videos/al_itkan/hr_recruitment_stage.xlsx')
        worksheet = workbook.add_worksheet()
        row = -1
        for i in temp:
            row = row+1
            worksheet.write(row, 0, str(i.id))
            worksheet.write(row, 1, str(i.is_interview))
            worksheet.write(row, 2, str(i.is_accepted))
        workbook.close()
        temp = self.env['hr.job'].search([])
        workbook = xlsxwriter.Workbook('/home/cybrosys/Videos/al_itkan/hr_job.xlsx')
        worksheet = workbook.add_worksheet()
        row = -1
        for i in temp:
            row = row + 1
            worksheet.write(row, 0, str(i.id))
            worksheet.write(row, 1, str(i.city))
            worksheet.write(row,2, str(i.opening_date))
            worksheet.write(row, 3, str(i.card_image))
            worksheet.write(row, 4, str(i.internal_ref))
            worksheet.write(row, 5, str(i.type_of_position))
            worksheet.write(row, 6, str(i.technical_knowledge))
            worksheet.write(row, 7, str(i.behavioral_competencies))
            worksheet.write(row, 8, str(i.education_language_requirements))
            worksheet.write(row, 9, str(i.private_job))
            worksheet.write(row, 10, str(i.notes))
        workbook.close()
        temp = self.env['product.template'].search([])
        workbook = xlsxwriter.Workbook('/home/cybrosys/Videos/al_itkan/product_template.xlsx')
        worksheet = workbook.add_worksheet()
        row = -1
        for i in temp:
            row = row + 1
            worksheet.write(row, 0, str(i.id))
            worksheet.write(row, 1, str(i.custom_country_of_origin))
            worksheet.write(row, 2, str(i.dangerous_goods))
            worksheet.write(row, 3, str(i.specifications))
            worksheet.write(row, 4, str(i.length))
        workbook.close()
        temp = self.env['hr.employee'].search([])
        workbook = xlsxwriter.Workbook('/home/cybrosys/Videos/al_itkan/hr_employee.xlsx')
        worksheet = workbook.add_worksheet()
        row = -1
        for i in temp:
            row = row + 1
            worksheet.write(row, 0, str(i.id))
            worksheet.write(row, 1, str(i.arabic_name))
            worksheet.write(row, 2, str(i.start_date))
            worksheet.write(row, 3, str(i.applicant_id))
            worksheet.write(row, 4, str(i.divisions))
            worksheet.write(row, 5, str(i.units))
            worksheet.write(row, 6, str(i.subunits))
        workbook.close()
        temp = self.env['hr.employee.public'].search([])
        workbook = xlsxwriter.Workbook('/home/cybrosys/Videos/al_itkan/hr_employee_public.xlsx')
        worksheet = workbook.add_worksheet()
        row = -1
        for i in temp:
            row = row + 1
            worksheet.write(row, 0, str(i.id))
            worksheet.write(row, 1, str(i.arabic_name))
            worksheet.write(row, 2, str(i.applicant_id))
            worksheet.write(row, 3, str(i.divisions))
            worksheet.write(row, 4, str(i.units))
            worksheet.write(row, 5, str(i.subunits))
        workbook.close()
        temp = self.env['hr.employee.public'].search([])
        workbook = xlsxwriter.Workbook('/home/cybrosys/Videos/al_itkan/hr_employee_public.xlsx')
        worksheet = workbook.add_worksheet()
        row = -1
        for i in temp:
            row = row + 1
            worksheet.write(row, 0, str(i.id))

            worksheet.write(row, 1, str(i.arabic_name))
            worksheet.write(row, 2, str(i.applicant_id.id))
            worksheet.write(row, 3, str(i.divisions))
            worksheet.write(row, 4, str(i.units))
            worksheet.write(row, 5, str(i.subunits))
        workbook.close()
        temp = self.env['calendar.event'].search([])
        workbook = xlsxwriter.Workbook('/home/cybrosys/Videos/al_itkan/calendar_event.xlsx')
        worksheet = workbook.add_worksheet()
        row = -1
        for i in temp:
            row = row + 1
            worksheet.write(row, 0, str(i.id))
            worksheet.write(row, 1, str(i.send_email_to_attendees))
        workbook.close()
        temp = self.env['purchase.order'].search([])
        workbook = xlsxwriter.Workbook('/home/cybrosys/Videos/al_itkan/purchase_order.xlsx')
        worksheet = workbook.add_worksheet()
        row = -1
        for i in temp:
            row = row + 1
            worksheet.write(row, 0, str(i.id))
            worksheet.write(row, 1, str(i.sent_prouduct_info))
        workbook.close()
        temp = self.env['purchase.order.line'].search([])
        workbook = xlsxwriter.Workbook('/home/cybrosys/Videos/al_itkan/purchase_order_line.xlsx')
        worksheet = workbook.add_worksheet()
        row = -1
        for i in temp:
            row = row + 1
            worksheet.write(row, 0, str(i.id))
            worksheet.write(row, 1, str(i.product_smn))
            worksheet.write(row, 2, str(i.serial_number))
            worksheet.write(row, 3, str(i.customer_id.id))
            worksheet.write(row, 4, str(i.brand_id.id))
        workbook.close()
        temp = self.env['sale.order'].search([])
        workbook = xlsxwriter.Workbook('/home/cybrosys/Videos/al_itkan/sale_order.xlsx')
        worksheet = workbook.add_worksheet()
        row = -1
        for i in temp:
            row = row + 1
            worksheet.write(row, 0, str(i.id))
            worksheet.write(row, 1, str(i.date_order))
            worksheet.write(row, 2, str(i.company_report_id.id))
        workbook.close()
        temp = self.env['sale.order.line'].search([])
        workbook = xlsxwriter.Workbook('/home/cybrosys/Videos/al_itkan/sale_order_line.xlsx')
        worksheet = workbook.add_worksheet()
        row = -1
        for i in temp:
            row = row + 1
            worksheet.write(row, 0, str(i.id))
            worksheet.write(row, 1, str(i.product_smn))
        workbook.close()
        temp = self.env['stock.quant'].search([])
        workbook = xlsxwriter.Workbook('/home/cybrosys/Videos/al_itkan/stock_quant.xlsx')
        worksheet = workbook.add_worksheet()
        row = -1
        for i in temp:
            row = row + 1
            worksheet.write(row, 0, str(i.id))
            worksheet.write(row, 1, str(i.lot_expire_date))
        workbook.close()
