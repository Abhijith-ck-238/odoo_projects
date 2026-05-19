# -*- coding: utf-8 -*-
from odoo import models, fields, api
from odoo.tools.translate import _
from odoo.exceptions import UserError
import datetime

"""Added by AhmedNaseem @IntegerEGRATEDPATH in 23/7/2020 , 
AL-ITKAN job Application form adjustment """


class ItkanJob(models.Model):
    _inherit="hr.job"

    city = fields.Char("City", related="address_id.city")
    opening_date = fields.Date(string="Vacancy Opening Date",default=datetime.datetime.now())
    card_image = fields.Binary(string="Vacany Card Image")
    internal_ref = fields.Char(string="Internal Reference",readonly=True)
    type_of_position = fields.Selection([("full_time", "Full Time"), ("part_time", "Part Time")],
        string="Type Of Position", default="full_time")
    technical_knowledge = fields.Text("Technical knowledge")
    behavioral_competencies = fields.Text("Behavioral Competencies")
    education_language_requirements = fields.Text("Education & Language Requirements")
    url = fields.Html("URL", compute="_get_url")
    private_job = fields.Boolean("PRIVATE JOB: ")
    notes = fields.Text("Notes")


    def _get_url(self):
        for rcd in self:
            rcd.url = f"""
                <a href='https://jobs.alitkan.com/jobs/description?job_id={rcd.id}' target='_blank'>
                    https://jobs.alitkan.com/jobs/description?job_id={rcd.id}</a>"""

    def set_recruit(self):
        self.opening_date = datetime.datetime.now()
        res = super(ItkanJob,self).set_recruit()
        return res


    def format_ref(self, year, month, id=False):
        if id:
            return year + month + f'{id:04}'
        else:
            return year + month


    @api.model
    def create(self,values):
        """Add Internal Reference"""
        today = datetime.date.today()
        month = today.strftime("%m")
        year = today.strftime("%y")
        jobs = self.env['hr.job'].search([('internal_ref', 'like', self.format_ref(year, month))], order="internal_ref desc")
        if not jobs:
            values.update({"internal_ref": self.format_ref(year, month, 1) })
        else:
            job = jobs[0]
            vaccany_number = int(job.internal_ref[4:8]) + 1
            formated_ref = self.format_ref(year, month, vaccany_number)
            values.update({"internal_ref": formated_ref})

        return super(ItkanJob, self).create(values)


class ItkanProduct(models.Model):
    _inherit="product.template"
    SELECTIONS=[("Dangerous Good","Dangerous Good"),("Dry Ice","Dry Ice")]

    custom_country_of_origin = fields.Char(string="Country of Origin")
    dangerous_goods = fields.Selection(SELECTIONS,string="Dangerous Goods and Storage")
    moq = fields.Integer(string="Minimum Order Quantity")
    specifications = fields.Char(string="Specification")
    length = fields.Char(string="length")

    
class ItkanEmployee(models.Model):
    _inherit = "hr.employee"
    
    arabic_name = fields.Char("الإسم العربي")
    start_date = fields.Date(related="contract_id.date_start")
    applicant_id = fields.Many2one("hr.applicant", "Employee Application")
    DIVISIONS = [("MD office", "MD office"), ("Technical","Technical"),("Sales","Sales"),("Finance","Finance"),("HRA","HRA"),("Logistics","Logistics")]
    UNITS = [("Arab North, Middle and South","Arab North, Middle and South"),
            ("Baghdad","Baghdad"),
            ("Cleaning Staff","Cleaning Staff"),
            ("DX","DX"),
            ("Enraff Meditron","Enraff Meditron"),
            ("Fleet","Fleet"),
            ("Fleet and Technicains","Fleet and Technicains"),
            ("Gettinge","Gettinge"),
            ("Guards","Guards"),
            ("Karl Storz","Karl Storz"),
            ("Karl Storz & DX","Karl Storz & DX"),
            ("Kimadia","Kimadia"),
            ("KRG","KRG"),
            ("Legal","Legal"),
            ("Medifa Maquet H&M","Medifa Maquet h&M"),
            ("Mindray","Mindray"),
            ("Modalities","Modalities"),
            ("North","North"),
            ("Packaging projects","Packaging projects"),
            ("Reception","Reception"),
            ("Resources","Resources"),
            ("Siemens Lab","Siemens Lab"),
            ("Siemens Radiology","Siemens Radiology"),
            ("Siemens US","Siemens US"),
            ("Social Marketing & Marcom","Social Marketing $ Marcom"),
            ("South","South"),
            ("Support Centre","Support Centre"),
            ("Technicians","Technicians"),
            ("Training","Training")]

    SUBUNITS=[("Arab North","Arab North"),
            ("AT","AT"),
            ("AT/MM","AT/MM"),
            ("Baghdad, karbalaa and Babel and Karkook","Baghdad, Karbalaa and Babel and Karkook"),
            ("Civil","Civil"),
            ("CT","CT"),
            ("CT/MM","CT/MM"),
            ("CT/PET CT","CT/PET CT"),
            ("DX","DX"),
            ("DX/MM","DX/MM"),
            ("Erbil","Erbil"),
            ("Erbil Office","Erbil Office"),
            ("Fleet","Fleet"),
            ("Fleet and Technicains","Fleet and Technicains"),
            ("IT/MM","IT/MM"),
            ("Karbalaa","Karbalaa"),
            ("KS","KS"),
            ("KS/MM","KS/MM"),
            ("Kut","Kut"),
            ("Mech.","Mech."),
            ("Mech./MM","Mech./MM"),
            ("MI/MM","MI/MM"),
            ("Mindray","Mindray"),
            ("Missan","Missan"),
            ("MM","MM"),
            ("MR","MR"),
            ("MR/MM","MR/MM"),
            ("OR","OR"),
            ("OR/MM","OR/MM"),
            ("Projects","Projects"),
            ("Siemens","Siemens"),
            ("Simawa","Simawa"),
            ("Soly","Soly"),
            ("Sulaymaniyah Office","Sulaymaniyah Office"),
            ("Technicians","Technicians"),
            ("TH","TH"),
            ("US","US"),
            ("XP","XP"),
            ("XP/MM","XP/MM")]


    divisions = fields.Selection(DIVISIONS,string="Division")
    units = fields.Selection(UNITS,string="Unit")
    subunits = fields.Selection(SUBUNITS,string="Subunit")

class EmployeePublic(models.Model):
    _inherit = 'hr.employee.public'

    arabic_name = fields.Char("الإسم العربي")
    applicant_id = fields.Many2one("hr.applicant", "Employee Application")
    DIVISIONS = [("MD office", "MD office"), ("Technical","Technical"),("Sales","Sales"),("Finance","Finance"),("HRA","HRA"),("Logistics","Logistics")]
    UNITS = [("Arab North, Middle and South","Arab North, Middle and South"),
            ("Baghdad","Baghdad"),
            ("Cleaning Staff","Cleaning Staff"),
            ("DX","DX"),
            ("Enraff Meditron","Enraff Meditron"),
            ("Fleet","Fleet"),
            ("Fleet and Technicains","Fleet and Technicains"),
            ("Gettinge","Gettinge"),
            ("Guards","Guards"),
            ("Karl Storz","Karl Storz"),
            ("Karl Storz & DX","Karl Storz & DX"),
            ("Kimadia","Kimadia"),
            ("KRG","KRG"),
            ("Legal","Legal"),
            ("Medifa Maquet H&M","Medifa Maquet h&M"),
            ("Mindray","Mindray"),
            ("Modalities","Modalities"),
            ("North","North"),
            ("Packaging projects","Packaging projects"),
            ("Reception","Reception"),
            ("Resources","Resources"),
            ("Siemens Lab","Siemens Lab"),
            ("Siemens Radiology","Siemens Radiology"),
            ("Siemens US","Siemens US"),
            ("Social Marketing & Marcom","Social Marketing $ Marcom"),
            ("South","South"),
            ("Support Centre","Support Centre"),
            ("Technicians","Technicians"),
            ("Training","Training")]

    SUBUNITS=[("Arab North","Arab North"),
            ("AT","AT"),
            ("AT/MM","AT/MM"),
            ("Baghdad, karbalaa and Babel and Karkook","Baghdad, Karbalaa and Babel and Karkook"),
            ("Civil","Civil"),
            ("CT","CT"),
            ("CT/MM","CT/MM"),
            ("CT/PET CT","CT/PET CT"),
            ("DX","DX"),
            ("DX/MM","DX/MM"),
            ("Erbil","Erbil"),
            ("Erbil Office","Erbil Office"),
            ("Fleet","Fleet"),
            ("Fleet and Technicains","Fleet and Technicains"),
            ("IT/MM","IT/MM"),
            ("Karbalaa","Karbalaa"),
            ("KS","KS"),
            ("KS/MM","KS/MM"),
            ("Kut","Kut"),
            ("Mech.","Mech."),
            ("Mech./MM","Mech./MM"),
            ("MI/MM","MI/MM"),
            ("Mindray","Mindray"),
            ("Missan","Missan"),
            ("MM","MM"),
            ("MR","MR"),
            ("MR/MM","MR/MM"),
            ("OR","OR"),
            ("OR/MM","OR/MM"),
            ("Projects","Projects"),
            ("Siemens","Siemens"),
            ("Simawa","Simawa"),
            ("Soly","Soly"),
            ("Sulaymaniyah Office","Sulaymaniyah Office"),
            ("Technicians","Technicians"),
            ("TH","TH"),
            ("US","US"),
            ("XP","XP"),
            ("XP/MM","XP/MM")]


    divisions = fields.Selection(DIVISIONS,string="Division")
    units = fields.Selection(UNITS,string="Unit")
    subunits = fields.Selection(SUBUNITS,string="Subunit")
   