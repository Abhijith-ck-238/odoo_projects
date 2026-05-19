from odoo import models, fields, api
from datetime import datetime
import calendar


class ItkApplForm(models.Model):
    _inherit = "hr.applicant"

    SKILL_LEVEL = [("not familiar", "Not Familiar"), ("beginner", "Beginner"), ("intermediate", "Intermediate"),
                   ("advanced", "Advanced"), ("expert", "Expert")]

    referral_source = fields.Selection(selection_add=[('none', 'None')])
    birth_month = fields.Char("Birth Month", compute='_compute_dob')
    birth_year = fields.Char("Birth Year", compute='_compute_dob')
    birth_day = fields.Char("Birth Day", compute='_compute_dob')
    is_fields_visible = fields.Boolean(compute="compute_is_fields_visible", store=True)

    @api.depends('partner_name')
    def compute_is_fields_visible(self):
        for rec in self:
            rec.is_fields_visible = self.env['ir.config_parameter'].sudo().get_param(
            'custom_recruitment.is_fields_visible')

    @api.depends('birthdate')
    def _compute_dob(self):
        for application in self:
            application.birth_month = application.birth_year = application.birth_day = False
            if application.birthdate:
                application.birth_month = calendar.month_name[application.birthdate.month]
                application.birth_year = application.birthdate.year
                application.birth_day = application.birthdate.day

    """ Personal Skills"""
    team_work_skill_level = fields.Selection(SKILL_LEVEL, string="Team Work")
    work_under_pressure_skill_level = fields.Selection(SKILL_LEVEL, string="Work Under Pressure")
    long_distance_travel_skill_level = fields.Selection(SKILL_LEVEL, string="Long Distance Travel")
    effective_communication_skill_level = fields.Selection(SKILL_LEVEL, string="Effective Communication")
    customer_relation_skill_level = fields.Selection(SKILL_LEVEL, string="Customer Relation")
    problem_solving_skill_level = fields.Selection(SKILL_LEVEL, string="Problem Solving")

    """ Computer Skills"""
    ms_dos_skill_level = fields.Selection(SKILL_LEVEL, string="Ms-dos")
    ms_windows_skill_level = fields.Selection(SKILL_LEVEL, string="Ms-windows")
    windows_server_skill_level = fields.Selection(SKILL_LEVEL, string="Windows Server")
    ms_word_skill_level = fields.Selection(SKILL_LEVEL, string="Ms word")
    ms_excel_skill_level = fields.Selection(SKILL_LEVEL, string="Ms excel")
    ms_power_point_skill_level = fields.Selection(SKILL_LEVEL, string="Ms Powerpoint")
    autocad_skill_level = fields.Selection(SKILL_LEVEL, string="Autocad")
    adobe_skill_level = fields.Selection(SKILL_LEVEL, string="Adobe Creative Cloud(Ps, Ai)")
    sql_skill_level = fields.Selection(SKILL_LEVEL, string="SQL")
    backend_dev_skill_level = fields.Selection(SKILL_LEVEL, string="Back-end Development")
    frontend_dev_skill_level = fields.Selection(SKILL_LEVEL, string="Front-end Development")

    """Networking Skills"""

    cabling_system = fields.Selection([("yes", "YES"), ("no", "NO")], "Structured Cabling System")
    cabling_system_skill_level = fields.Selection(SKILL_LEVEL, "Structured Cabling System Skill Level")
    network_device = fields.Selection([("hub", "Hub"), ("switch", "Switch"), ("router", "Router"),
                                       ("firewall", "Firewall")], "Familiar Network Device")
    wireless_network = fields.Selection([("yes", "YES"), ("no", "NO")], "Wireless Network")
    wireless_network_skill_level = fields.Selection(SKILL_LEVEL, "Wireless Network Skill Level")
    wireless_device = fields.Selection([("wireless lan card", "Wireless LAN Card"), ("access point", "Access Point"),
                                        ("wireless router", "Wireless Router"), ("outdoor antena", "Outdoor Antena")],
                                       "Wireless Device")

    """Related Employee"""
    related_employee = fields.Selection([("yes", "YES"), ("no", "NO")],
                                        string="Are any of your relatives or friends Employed in our company?")
    related_employee_name = fields.Char(string="If yes please give their name")
    related_employee_relation = fields.Char(string="Relation")

    job_responsibilities = fields.Char(string="Job Responsibilities")
    job_responsibilities_0 = fields.Char(string="Job Responsibilities")
    job_responsibilities_1 = fields.Char(string="Job Responsibilities")

    """Education"""
    other_0_major = fields.Char(string="Major ")
    other_1_major = fields.Char(string="Major ")

    """Emergency Contact"""
    emergency_contact_name = fields.Char(string="Full Name")
    emergency_contact_phone = fields.Char(string="Phone No")
    emergency_contact_relation = fields.Char(string="Relation")
    c_skill_erp = fields.Char(string="ERP")
    c_skill_other = fields.Char(string="Other")
    past_interview_date = fields.Date(string="Past interview date")
