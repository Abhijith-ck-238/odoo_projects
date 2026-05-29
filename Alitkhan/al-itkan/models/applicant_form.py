from odoo import models, fields, api
from odoo.exceptions import UserError
from odoo.tools.translate import _
import datetime


class ItkApplForm(models.Model):
    _inherit = "hr.applicant"

    filling_time = fields.Char("Filling Time", readonly=True, help="Time it took for applicant to fill out the form")

    SKILL_LEVEL = [("not familiar", "Not Familiar"),
                   ("beginner", "Beginner"),
                   ("intermediate", "Intermediate"),
                   ("advanced", "Advanced"),
                   ("expert", "Expert")]

    """ Personal Details """

    surname = fields.Char(string="Surname", help="Applicant Surname")
    arabic_name = fields.Char(string="Arabic Name")
    address = fields.Char(string="address", help="Applicant Address")
    hai = fields.Char(string="Hai", help="address - Hai")
    sec = fields.Char(string="Sec.", help="address - Sec")
    st = fields.Char(string="Street", help="address - Street")
    house = fields.Char(string="House", help="address - house No.")
    nearest = fields.Char(string="Nearest POR", help="Nearest point of reference to the applicant address")
    birthdate = fields.Date(string="Birthdate")
    place_of_birth = fields.Char(string="Place of Birth")
    gender = fields.Selection([("male", "Male"), ("female", "Female")])
    height = fields.Integer(string="Height")
    weight = fields.Integer(string="Weigh")
    citizenship = fields.Char(string="Citizenship")
    religion = fields.Char(string="Religion")
    social_status = fields.Selection([("single", "Single"),
                                      ("engaged", "Engaged"),
                                      ("married", "Married"),
                                      ("seperated", "Seperated"),
                                      ("widowed", "Widowed"),
                                      ("divorced", "Divorced")])

    """Family Information"""

    father_profession = fields.Char(string="Father`s Profession")
    mother_profession = fields.Char(string="Mother`s Profession")

    first_name = fields.Char(string="First Name")
    profession = fields.Char(string="Profession")

    first_name_0 = fields.Char(string="First Name")
    profession_0 = fields.Char(string="Profession")

    first_name_1 = fields.Char(string="First Name")
    profession_1 = fields.Char(string="Profession")

    first_name_2 = fields.Char(string="First Name")
    profession_2 = fields.Char(string="Profession")

    first_name_3 = fields.Char(string="First Name")
    profession_3 = fields.Char(string="Profession")

    first_name_4 = fields.Char(string="First Name")
    profession_4 = fields.Char(string="Profession")

    first_name_5 = fields.Char(string="First Name")
    profession_5 = fields.Char(string="Profession")

    first_name_6 = fields.Char(string="First Name")
    profession_6 = fields.Char(string="Profession")

    """ Health and Limitations """
    health_status = fields.Selection([("excellent", "Excellent"),
                                      ("good", "Good"),
                                      ("average", "Average"),
                                      ("below average", "Below Average"),
                                      ("poor", "Poor"),
                                      ("very poor", "Very Poor")], string="Your Health Status?")

    """ Have you suffered or are you suffering from any Terminal Illness or Chronic Disease?"""
    disease = fields.Selection([("yes", "YES"), ("no", "NO")],
                               help="Have the applicant ever suffered from Illness or disease")

    """ Are there any limitations on your ability to perform in your prospective field of work?"""
    limitaions = fields.Selection([("yes", "YES"), ("no", "NO")],
                                  help="Are there any limitations on your ability to perform in your prospective field of work?")

    """Are there any limitations on your ability to engage in all types of travel? Inside or outside Iraq"""
    limitaions_travel = fields.Selection([("yes", "YES"), ("no", "NO")],
                                         help="Are there any limitations on your ability to engage in all types of travel? Inside or outside Iraq?")

    """ Languages and level of Proficiency """
    """ Please Rate your Language Skills on the following scale:
 (1) Excellent (2) Very Good (3) Good (4) Average (5) Below Average (6) Poor (7) Very Poor """

    """ Arabic """

    ar_r = fields.Integer(string="Reading")
    ar_w = fields.Integer(string="Writing")
    ar_s = fields.Integer(string="Speaking")
    ar_u = fields.Integer(string="Understanding")
    ar_o = fields.Integer(string="Overall")

    """ English """

    en_r = fields.Integer(string="Reading")
    en_w = fields.Integer(string="Writing")
    en_s = fields.Integer(string="Speaking")
    en_u = fields.Integer(string="Understanding")
    en_o = fields.Integer(string="Overall")

    """ Other """

    other_name_0 = fields.Char(string="Name")
    other_r_0 = fields.Integer(string="Reading")
    other_w_0 = fields.Integer(string="Writing")
    other_s_0 = fields.Integer(string="Speaking")
    other_u_0 = fields.Integer(string="Understanding")
    other_o_0 = fields.Integer(string="Overall")

    """ Other 1 """

    other_name_1 = fields.Char(string="Name")
    other_r_1 = fields.Integer(string="Reading")
    other_w_1 = fields.Integer(string="Writing")
    other_s_1 = fields.Integer(string="Speaking")
    other_u_1 = fields.Integer(string="Understanding")
    other_o_1 = fields.Integer(string="Overall")

    """ Education """
    primary_name = fields.Char(string="Name")
    primary_years = fields.Char(string="# of Years")
    primary_avg = fields.Integer(string="Average(%)")

    Intermediate_name = fields.Char(string="Integerermediate")
    Intermediate_years = fields.Char(string="# of Years")
    Intermediate_avg = fields.Integer(string="Average(%)")

    secondary_name = fields.Char(string="Secondary")
    secondary_years = fields.Char(string="# of Years")
    secondary_avg = fields.Integer(string="Average(%)")

    college_name = fields.Char(string="College or Institte")
    college_major = fields.Char(string="Major")
    college_years = fields.Char(string="# of Years")
    college_avg = fields.Integer(string="Average(%)")

    other_0_name = fields.Char(string="Other ")
    other_0_years = fields.Char(string="# of Years")
    other_0_avg = fields.Integer(string="Average(%)")

    other_1_name = fields.Char(string="Other 1")
    other_1_years = fields.Char(string="# of Years")
    other_1_avg = fields.Integer(string="Average(%)")

    highest_acad = fields.Char(string="Highest Academic Qualification")
    major = fields.Char(string="Major")
    highest_grad_year = fields.Char(string="Graduation Year")
    highest_uni = fields.Char(string="University")
    highest_country = fields.Char(string="Country")

    """ Referral Info """
    referral_source = fields.Selection([("walk-in", "Walk-In"),
                                        ("employee", "Employee"),
                                        ("facebook", "Facebook"),
                                        ("linked-in", "Linked-In")])

    other_referral_source = fields.Char(string="Other Referral Source")

    preffered_fow = fields.Selection([("technical", "Technical"),
                                      ("sales", "Sales"),
                                      ("administration", "Administration")], help="Preffered Field of work")

    preferred_cp = fields.Selection([("3 years", "3 Years"),
                                     ("5 years", "5 Years"),
                                     ("10 years", "10 Years")], help="Preferred contract Period")

    """ Technical Skills """

    skill_0_Desc = fields.Char(string="Skill description")
    skill_0_level = fields.Selection(SKILL_LEVEL, string="Skill level")

    skill_1_Desc = fields.Char(string="Skill description")
    skill_1_level = fields.Selection(SKILL_LEVEL, string="Skill level")

    skill_2_Desc = fields.Char(string="Skill description")
    skill_2_level = fields.Selection(SKILL_LEVEL, string="Skill level")

    skill_3_Desc = fields.Char(string="Skill description")
    skill_3_level = fields.Selection(SKILL_LEVEL, string="Skill level")

    skill_4_Desc = fields.Char(string="Skill description")
    skill_4_level = fields.Selection(SKILL_LEVEL, string="Skill level")

    skill_5_Desc = fields.Char(string="Skill description")
    skill_5_level = fields.Selection(SKILL_LEVEL, string="Skill level")

    """ Administration Skills """

    business_correspondence_skill_level = fields.Selection(SKILL_LEVEL, string="Business Corrispondence")
    effective_communication_skill_level = fields.Selection(SKILL_LEVEL, string="Effective Communication")
    customer_service_skill_level = fields.Selection(SKILL_LEVEL, string="Customer Service")
    team_work_skill_level = fields.Selection(SKILL_LEVEL, string="Team Work")
    Internet_and_research_skill_level = fields.Selection(SKILL_LEVEL, string="Internet and Research")
    ms_office_and_outlook_skill_level = fields.Selection(SKILL_LEVEL, string="MS office and Outlook")
    office_machine_skill_level = fields.Selection(SKILL_LEVEL, string="Office Equipment")
    typing_skill_level = fields.Selection(SKILL_LEVEL, string="Typing")
    time_management_skill_level = fields.Selection(SKILL_LEVEL, string="Time Management")
    attention_to_detail_level = fields.Selection(SKILL_LEVEL, string="Attention to Details")
    goal_oriented_skill_level = fields.Selection(SKILL_LEVEL, string="Goal Oriented")
    multi_tasking_skill_level = fields.Selection(SKILL_LEVEL, string="Multitasking")
    follow_up_skill_level = fields.Selection(SKILL_LEVEL, string="Follow-up Skills")
    employee_relation_skill_level = fields.Selection(SKILL_LEVEL, string="Employee Relations")
    supervision_skill_level = fields.Selection(SKILL_LEVEL, string="Supervision")

    """ Sales Skills """

    relationship_building_skill_level = fields.Selection(SKILL_LEVEL, string="RelationShip building skill level")
    time_management_skill_level = fields.Selection(SKILL_LEVEL, string="Time Management skill level")
    research_information_gathering_skill_level = fields.Selection(SKILL_LEVEL,
                                                                  string="Research and information gethering skill level")
    medical_product_knowledge_skill_level = fields.Selection(SKILL_LEVEL,
                                                             string="Medical product knowledge skill level")
    business_communication_skill_level = fields.Selection(SKILL_LEVEL, string="Business communication skill level")
    client_engagement_skill_level = fields.Selection(SKILL_LEVEL, string="Client management skill level")
    sales_presentations_demos_skill_level = fields.Selection(SKILL_LEVEL, string="Sales presentation skill level")
    contract_negotiation_skill_level = fields.Selection(SKILL_LEVEL, string="Contact negotiation skill level")
    closing_skills_skill_level = fields.Selection(SKILL_LEVEL, string="Closing skills skill level")
    self_motivated_ambitious_skill_level = fields.Selection(SKILL_LEVEL, string="Self motivation")
    adaptability_skill_level = fields.Selection(SKILL_LEVEL, string="Adaptability skill level")
    responsibility_skill_level = fields.Selection(SKILL_LEVEL, string="Responsibility skill level")
    goal_oriented_skill_level = fields.Selection(SKILL_LEVEL, string="Goal oriented skill level")
    passionate_about_selling_skill_level = fields.Selection(SKILL_LEVEL, string="Passion about selling")

    "Training and Certifications"

    t0 = fields.Char(string="Certifiacate 1")
    t0_year = fields.Char(string="Year")
    t0_awarded_by = fields.Char(string="Awarded By")
    t0_country_city = fields.Char(string="Country/City")

    t1 = fields.Char(string="Certifiacate 2")
    t1_year = fields.Char(string="Year")
    t1_awarded_by = fields.Char(string="Awarded By")
    t1_country_city = fields.Char(string="Country/City")

    t2 = fields.Char(string="Certifiacate 3")
    t2_year = fields.Char(string="Year")
    t2_awarded_by = fields.Char(string="Awarded By")
    t2_country_city = fields.Char(string="Country/City")

    t3 = fields.Char(string="Certifiacate 4")
    t3_year = fields.Char(string="Year")
    t3_awarded_by = fields.Char(string="Awarded By")
    t3_country_city = fields.Char(string="Country/City")

    t4 = fields.Char(string="Certifiacate 5")
    t4_year = fields.Char(string="Year")
    t4_awarded_by = fields.Char(string="Awarded By")
    t4_country_city = fields.Char(string="Country/City")

    t5 = fields.Char(string="Certifiacate 6")
    t5_year = fields.Char(string="Year")
    t5_awarded_by = fields.Char(string="Awarded By")
    t5_country_city = fields.Char(string="Country/City")

    """ Employment History """

    contact_disclaimer = fields.Boolean(string="Can we contact your previous employer(s) ?")

    employer_name = fields.Char(string="Employer Names")
    job_title = fields.Char(string="Job Title")
    employer_address = fields.Char(string="Employer addres")
    employer_province = fields.Char(string="Employer Province")
    from_date = fields.Date(string="From")
    to_date = fields.Date(string="To")
    starting_slry = fields.Integer(string="Starting Salary")
    ending_slry = fields.Integer(string="Last Salary")
    supervisor = fields.Char(string="Supervisor")
    super_phone = fields.Char(string="Supervisor Phone No.")
    reason_for_leaving = fields.Char(string="Reason for Leaving")

    employer_name_0 = fields.Char(string="Employer Names")
    job_title_0 = fields.Char(string="Job Title")
    employer_address_0 = fields.Char(string="Employer addres")
    employer_province_0 = fields.Char(string="Employer Province")
    from_date_0 = fields.Date(string="From")
    to_date_0 = fields.Date(string="To")
    starting_slry_0 = fields.Integer(string="Starting Salary")
    ending_slry_0 = fields.Integer(string="Last Salary")
    supervisor_0 = fields.Char(string="Supervisor")
    super_phone_0 = fields.Char(string="Supervisor Phone No.")
    reason_for_leaving_0 = fields.Char(string="Reason for Leaving")

    employer_name_1 = fields.Char(string="Employer Names")
    job_title_1 = fields.Char(string="Job Title")
    employer_address_1 = fields.Char(string="Employer addres")
    employer_province_1 = fields.Char(string="Employer Province")
    from_date_1 = fields.Date(string="From")
    to_date_1 = fields.Date(string="To")
    starting_slry_1 = fields.Integer(string="Starting Salary")
    ending_slry_1 = fields.Integer(string="Last Salary")
    supervisor_1 = fields.Char(string="Supervisor")
    super_phone_1 = fields.Char(string="Supervisor Phone No.")
    reason_for_leaving_1 = fields.Char(string="Reason for Leaving")

    """ Additional Information """
    union_member = fields.Selection([("yes", "YES"), ("no", "NO")],
                                    string="Are you a member of the Iraqi Engineers union?")
    union_member_date = fields.Date("If yes Sense when were you a memeber ?")
    driver_license = fields.Selection([("yes", "YES"), ("no", "NO")], string="Do you have a valid drivers license?")
    driver_license_date = fields.Date(string="Driver license issue Date")
    means_of_transport = fields.Char(string="What is your means of transport?(Personal Car, Public, etc.")
    good_appoint = fields.Selection([("yes", "YES"), ("no", "NO")], string="Are you good with keeping appointments?")
    smoking = fields.Selection([("yes", "YES"), ("no", "NO")], string="Do you smoke?")
    long_hours = fields.Selection([("yes", "YES"), ("no", "NO")], string="Can you handle long work hours?")
    start_date = fields.Date(string="What is your preferred start date?")
    planning_to_study = fields.Selection([("yes", "YES"), ("no", "NO")],
                                         string="do you plan to complete studies, currently or in the future?")
    presently_employed = fields.Selection([("yes", "YES"), ("no", "NO")], string="Are you currently employed?")
    contact_employer = fields.Selection([("yes", "YES"), ("no", "NO")], string="Can we contact your past employers?")

    "Skills 2"
    SKILLS_SET_2 = [("excellent", "Excellent"),
                    ("very_good", "Very Good"),
                    ("good", "Good"),
                    ("average", "Average"),
                    ("below_average", "Below Average"),
                    ("poor", "Poor"),
                    ("very_poor", "Very Poor")]

    team_work = fields.Selection(SKILLS_SET_2, string="Team Work skills")
    pressure = fields.Selection(SKILLS_SET_2, string="Work under pressure")
    travel = fields.Selection(SKILLS_SET_2, string="Ability To Travel")

    """ references non relatives  """

    ref_name = fields.Char(string="Name")
    ref_relation = fields.Char(string="Relation")
    ref_phone = fields.Char(string="Phone No.")

    ref_name_1 = fields.Char(string="Name")
    ref_relation_1 = fields.Char(string="Relation")
    ref_phone_1 = fields.Char(string="Phone No.")

    """ refrences Relatives """

    ref_r_name = fields.Char(string="Name")
    ref_r_relation = fields.Char(string="Relation")
    ref_r_phone = fields.Char(string="Phone No.")

    ref_r_name_1 = fields.Char(string="Name")
    ref_r_relation_1 = fields.Char(string="Relation")
    ref_r_phone_1 = fields.Char(string="Phone No.")

    """ Signature """
    signature = fields.Char(string="Please sign your name")
    sig_date = fields.Date(string="Date")

    """ Supporting Documents """
    photo = fields.Binary(string="Photo")
    national_id = fields.Binary(string="National ID")
    citizenship_cert = fields.Binary(string="Citizenship Certificate")
    accomodation_id = fields.Binary(string="Accomidation ID")
    uni_degree = fields.Binary(string="University Degree")
    medical = fields.Binary(string="Medical Test")
    no_crim_req = fields.Binary(string="No Criminal Record")
    letter_rec_1 = fields.Binary(string="Letter of Recommendation 1")
    letter_rec_2 = fields.Binary(string="Letter of Recommendation 2")
    cv = fields.Binary(string="CV")

    """ Supporting Documents File Names """
    photo_filename = fields.Char(
        string="Photo", compute="_get_photo_filename")
    national_id_filename = fields.Char(
        string="National ID", compute="_get_national_id_filename")
    citizenship_cert_filename = fields.Char(
        string="Citizenship Certificate", compute="_get_citizenship_cert_filename")
    accomodation_id_filename = fields.Char(
        string="Accomidation ID", compute="_get_accomodation_id_filename")
    uni_degree_filename = fields.Char(
        string="University Degree", compute="_get_uni_degree_filename")
    medical_filename = fields.Char(
        string="Medical Test", compute="_get_medical_filename")
    no_crim_req_filename = fields.Char(
        string="No Criminal Record", compute="_get_no_crim_req_filename")
    letter_rec_1_filename = fields.Char(
        string="Letter of Recommendation 1", compute="_get_letter_rec_1_filename")
    letter_rec_2_filename = fields.Char(
        string="Letter of Recommendation 2", compute="_get_letter_rec_2_filename")
    cv_filename = fields.Char(
        string="CV", compute="_get_cv_filename")

    def _get_photo_filename(self):
        self.photo_filename = f"{self.partner_name} - {self.external_ref} - Photo" if self.external_ref \
            else f"{self.partner_name} - Photo"

    def _get_national_id_filename(self):
        self.national_id_filename = f"{self.partner_name} - {self.external_ref} - National ID" if self.external_ref \
            else f"{self.partner_name} - National ID"

    def _get_citizenship_cert_filename(self):
        self.citizenship_cert_filename = f"{self.partner_name} - {self.external_ref} - Citizenship Certificate" if self.external_ref \
            else f"{self.partner_name} - Citizenship Certificate"

    def _get_accomodation_id_filename(self):
        self.accomodation_id_filename = f"{self.partner_name} - {self.external_ref} - Accomidation ID" if self.external_ref \
            else f"{self.partner_name} - Accomidation ID"

    def _get_uni_degree_filename(self):
        self.uni_degree_filename = f"{self.partner_name} - {self.external_ref} - University Degree" if self.external_ref \
            else f"{self.partner_name} - University Degree"

    def _get_medical_filename(self):
        self.medical_filename = f"{self.partner_name} - {self.external_ref} - Medical Test" if self.external_ref \
            else f"{self.partner_name} - Medical Test"

    def _get_no_crim_req_filename(self):
        self.no_crim_req_filename = f"{self.partner_name} - {self.external_ref} - No Criminal Record" if self.external_ref \
            else f"{self.partner_name} - No Criminal Record"

    def _get_letter_rec_1_filename(self):
        self.letter_rec_1_filename = f"{self.partner_name} - {self.external_ref} - Letter of Recommendation 1" if self.external_ref \
            else f"{self.partner_name} - Letter of Recommendation 1"

    def _get_letter_rec_2_filename(self):
        self.photo_filename = f"{self.partner_name} - {self.external_ref} - Letter of Recommendation 2" if self.external_ref \
            else f"{self.partner_name} - Letter of Recommendation 2"

    def _get_cv_filename(self):
        self.cv_filename = f"{self.partner_name} - {self.external_ref} - CV" if self.external_ref \
            else f"{self.partner_name} - CV"

    skype_id = fields.Char(string="Skype ID")
    external_ref = fields.Char(string="External Reference")

    is_accepted = fields.Boolean(
        "Is Accepted ?", related="stage_id.is_accepted")
    is_interview = fields.Boolean(
        "Is Interview ?", related="stage_id.is_interview")

    @api.model
    def create(self, values):
        BINARY_FILES = [('photo', 'Photo'), ('national_id', "National ID"),
                        ('citizenship_cert', "Citizenship Certificate"),
                        ('accomodation_id', "Accomodation ID"), ('uni_degree', "University Degree"),
                        ('medical', "Medical Record"),
                        ('no_crim_req', "No Criminal Record Proof"), ('letter_rec_1', "Letter Of Recommendation 1"),
                        ('letter_rec_2', "Letter Of Recommendation 2"),
                        ('cv', "CV")]
        record = super(ItkApplForm, self).create(values)
        # raise UserError(str(values))
        for attach in BINARY_FILES:
            if values.get(attach[0]):
                record.message_post(body="%s Attachment" % (attach[1]),
                                    attachments=[(attach[1] + '.pdf', values[attach[0]])])
            else:
                pass
        return record

    def write(self, values):
        BINARY_FILES = [('photo', 'Photo'), ('national_id', "National ID"),
                        ('citizenship_cert', "Citizenship Certificate"),
                        ('accomodation_id', "Accomodation ID"), ('uni_degree', "University Degree"),
                        ('medical', "Medical Record"),
                        ('no_crim_req', "No Criminal Record Proof"), ('letter_rec_1', "Letter Of Recommendation 1"),
                        ('letter_rec_2', "Letter Of Recommendation 2"),
                        ('cv', "CV")]
        for attach in BINARY_FILES:
            if attach[0] in values:
                self.message_post(body="%s Attachment" % (attach[1]),
                                  attachments=[(attach[1] + '.pdf', values[attach[0]])])
            else:
                pass
        res = super(ItkApplForm, self).write(values)
        return res

    def create_employee_from_applicant(self):
        """ Create an hr.employee from the hr.applicants """
        employee = False
        for applicant in self:
            contact_name = False
            if applicant.partner_id:
                address_id = applicant.partner_id.address_get(['contact'])['contact']
                contact_name = applicant.partner_id.display_name
            else:
                if not applicant.partner_name:
                    raise UserError(_('You must define a Contact Name for this applicant.'))
                new_partner_id = self.env['res.partner'].create({
                    'is_company': False,
                    'name': applicant.partner_name,
                    'email': applicant.email_from,
                    'phone': applicant.partner_phone,
                    'mobile': applicant.partner_mobile
                })
                address_id = new_partner_id.address_get(['contact'])['contact']
            if applicant.partner_name or contact_name:
                employee = self.env['hr.employee'].create({
                    'name': applicant.partner_name or contact_name,
                    'job_id': applicant.job_id.id or False,
                    'job_title': applicant.job_id.name or False,
                    'private_street': address_id or False,
                    'department_id': applicant.department_id.id or False,
                    'address_id': applicant.company_id and applicant.company_id.partner_id
                                  and applicant.company_id.partner_id.id or False,
                    'work_email': applicant.department_id and applicant.department_id.company_id
                                  and applicant.department_id.company_id.email or False,
                    'work_phone': applicant.department_id and applicant.department_id.company_id
                                  and applicant.department_id.company_id.phone or False,
                    'applicant_id': applicant.id  # edited
                })
                applicant.write({'employee_id': employee.id})
                if applicant.job_id:
                    applicant.job_id.write({'no_of_hired_employee': applicant.job_id.no_of_hired_employee + 1})
                    applicant.job_id.message_post(
                        body=_(
                            'New Employee %s Hired') % applicant.partner_name if applicant.partner_name else applicant.name,
                        subtype_xmlid="hr_recruitment.mt_job_applicant_hired")
                applicant.message_post(
                    body=_(
                        'New Employee %s Hired') % applicant.partner_name if applicant.partner_name else applicant.name,
                    subtype_id=self.env.ref("hr_recruitment.mt_applicant_hired").id)
                # applicant.message_post_with_view(
                #     'hr_recruitment.applicant_hired_template',
                #     values={'applicant': applicant},
                #     subtype_id=self.env.ref("hr_recruitment.mt_applicant_hired").id)

        employee_action = self.env.ref('hr.open_view_employee_list')
        dict_act_window = employee_action.read([])[0]
        dict_act_window['context'] = {'form_view_initial_mode': 'edit'}
        dict_act_window['res_id'] = employee.id
        return dict_act_window

    def button_approve(self):
        accepted_stage = self.env['hr.recruitment.stage'].search([
            ('is_accepted', '=', True)],limit=1)
        for record in self:
            record.stage_id = accepted_stage
