from odoo import models, fields, api, tools, _
from odoo.exceptions import AccessError


class ResUsersExtend(models.AbstractModel):
    _inherit = 'res.users'

    SELF_WRITEABLE_FIELDS = ['passport',
                             'photo',
                             'marriage_certificate',
                             'old_schengen_visa',
                             'sanad',
                             'bank_statement',
                             'driving_license',
                             'graduation_certificate',
                             'housing_card',
                             'ration_card',
                             'family_ids',
                             'family_passports',
                             'unified_card_nationality', ]
    # User can read a few of his own fields
    SELF_READABLE_FIELDS = ['passport',
                            'photo',
                            'marriage_certificate',
                            'old_schengen_visa',
                            'sanad',
                            'bank_statement',
                            'driving_license',
                            'graduation_certificate',
                            'housing_card',
                            'ration_card',
                            'family_ids',
                            'family_passports',
                            'unified_card_nationality', ]

    # User can write a few of his own fields

    passport = fields.Binary(string="Passport", related='employee_id.passport',
                             readonly=False)
    photo = fields.Binary(string="Photo", related='employee_id.photo',
                          readonly=False)
    marriage_certificate = fields.Binary(string="Marriage Certificate",
                                         related='employee_id.marriage_certificate',
                                         readonly=False)
    old_schengen_visa = fields.Binary(string="Passport",
                                      related='employee_id.old_schengen_visa',
                                      readonly=False)
    sanad = fields.Binary(string="Old Schengen Visa",
                          related='employee_id.sanad', readonly=False,
                          )
    bank_statement = fields.Binary(string="Bank Statement",
                                   related='employee_id.bank_statement',
                                   readonly=False)
    driving_license = fields.Binary(string="Driving License",
                                    related='employee_id.driving_license',
                                    readonly=False)
    graduation_certificate = fields.Binary(string="Graduation Certificate",
                                           related='employee_id.graduation_certificate',
                                           readonly=False)
    housing_card = fields.Binary(string="بطاقة سكن",
                              related='employee_id.housing_card', readonly=False)
    ration_card = fields.Binary(related='employee_id.ration_card',
                                  readonly=False,
                                  string="بطاقة تموينية ")

    unified_card_nationality = fields.Many2many(
        related='employee_id.unified_card_nationality', readonly=False,
        string="بطاقة موحدة او شهادة جنسية وهوية")

    family_ids = fields.Many2many(related='employee_id.family_ids',
                                  readonly=False,
                                  string="Family IDs")

    family_passports = fields.Many2many(related='employee_id.family_passports',
                                        readonly=False,
                                        string="Family Passports")

    def _self_readable_fields(self):
        """ Override to add custom readable fields in Odoo 18 """
        hr_readable_fields = [
            'additional_note', 'address_id', 'barcode', 'birthday', 'category_ids', 'children', 'coach_id',
            'country_of_birth', 'department_id', 'display_name', 'emergency_contact', 'emergency_phone',
            'employee_bank_account_id', 'employee_country_id', 'gender', 'identification_id', 'job_title',
            'private_email', 'km_home_work', 'marital', 'mobile_phone', 'employee_parent_id', 'passport_id',
            'permit_no', 'pin', 'place_of_birth', 'spouse_birthdate', 'spouse_complete_name', 'visa_expire',
            'visa_no', 'work_email', 'work_phone', 'certificate', 'study_field', 'study_school', 'active',
            'child_ids', 'employee_id', 'employee_ids', 'hr_presence_state', 'last_activity', 'last_activity_time',
            'can_edit', 'passport', 'photo', 'marriage_certificate', 'old_schengen_visa', 'sanad', 'bank_statement',
            'driving_license', 'graduation_certificate', 'housing_card', 'ration_card', 'family_ids',
            'family_passports',
            'unified_card_nationality'
        ]

        return super()._self_readable_fields() | set(hr_readable_fields)

    def _self_writeable_fields(self):
        """ Override to add custom writable fields in Odoo 18 """
        hr_writable_fields = [
            'passport', 'photo', 'marriage_certificate', 'old_schengen_visa', 'sanad', 'bank_statement',
            'driving_license', 'graduation_certificate', 'housing_card', 'ration_card', 'family_ids',
            'family_passports', 'unified_card_nationality'
        ]

        return super()._self_writeable_fields() | set(hr_writable_fields)



    def write(self, vals):
        """
        Synchronize user and its related employee
        and check access rights if employees are not allowed to update
        their own data (otherwise sudo is applied for self data).
        """
        can_edit_self = self.env['ir.config_parameter'].sudo().get_param(
            'hr.hr_employee_self_edit')
        result = super(ResUsersExtend, self).write(vals)
        employee_values = {}
        for fname in [f for f in ['name', 'email', 'image_1920', 'tz',
                                  'passport',
                                  'photo',
                                  'marriage_certificate',
                                  'old_schengen_visa',
                                  'sanad',
                                  'bank_statement',
                                  'driving_license',
                                  'graduation_certificate',
                                  'housing_card',
                                  'ration_card',
                                  'family_ids',
                                  'family_passports',
                                  'unified_card_nationality',
                                  ] if f in vals]:
            employee_values[fname] = vals[fname]
        if employee_values:
            if 'email' in employee_values:
                employee_values['work_email'] = employee_values.pop('email')
            if 'image_1920' in vals:
                without_image = self.env['hr.employee'].sudo().search(
                    [('user_id', 'in', self.ids),
                     ('image_1920', '=', False)])
                with_image = self.env['hr.employee'].sudo().search(
                    [('user_id', 'in', self.ids),
                     ('image_1920', '!=', False)])
                without_image.write(employee_values)
                if not can_edit_self:
                    employee_values.pop('image_1920')
                with_image.write(employee_values)
            else:
                self.env['hr.employee'].sudo().search(
                    [('user_id', 'in', self.ids)]).write(employee_values)
        return result
