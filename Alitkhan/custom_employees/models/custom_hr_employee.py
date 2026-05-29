from odoo import models, fields, api,_
from odoo.tools.float_utils import float_round


class HrEmployeeExtend(models.Model):
    _inherit = 'hr.employee'

    passport = fields.Binary(string="Passport")
    photo = fields.Binary(string="Photo")
    marriage_certificate = fields.Binary(string="Marriage Certificate")
    old_schengen_visa = fields.Binary(string="Passport")
    sanad = fields.Binary(string="Old Schengen Visa")
    bank_statement = fields.Binary(string="Bank Statement")
    driving_license = fields.Binary(string="Driving License")
    graduation_certificate = fields.Binary(string="Graduation Certificate")
    housing_card = fields.Binary(string="بطاقة سكن")
    ration_card = fields.Binary(string="بطاقة تموينية ")

    unified_card_nationality = fields.Many2many(
        comodel_name="ir.attachment",
        relation="attachement_employee_docs_rel",
        column1="employee_id",
        column2="attachment_id",
        string="بطاقة موحدة او شهادة جنسية وهوية")

    family_ids = fields.Many2many(comodel_name="ir.attachment",
                                  relation="attachement_employee_family_ids_docs_rel",
                                  column1="employee_id",
                                  column2="attachment_id",
                                  string="Family IDs")

    family_passports = fields.Many2many(comodel_name="ir.attachment",
                                        relation="attachement_employee_family_passports_docs_rel",
                                        column1="employee_id",
                                        column2="attachment_id",
                                        string="Family Passports")

    new_divisions = fields.Many2one('division.division', string="Division new")
    new_units = fields.Many2one('unit.unit', string="Units")
    is_set_division_and_unit_visible = fields.Boolean(
        compute='compute_is_set_division_and_unit_visible')
    DIVISIONS = [("MD office", "MD office"), ("Technical", "Technical"),
                 ("Sales", "Sales"), ("Finance", "Finance"), ("HRA", "HRA"),
                 ("Logistics", "Logistics")]
    UNITS = [("Arab North, Middle and South", "Arab North, Middle and South"),
             ("Baghdad", "Baghdad"),
             ("Cleaning Staff", "Cleaning Staff"),
             ("DX", "DX"),
             ("Enraff Meditron", "Enraff Meditron"),
             ("Fleet", "Fleet"),
             ("Fleet and Technicains", "Fleet and Technicains"),
             ("Gettinge", "Gettinge"),
             ("Guards", "Guards"),
             ("Karl Storz", "Karl Storz"),
             ("Karl Storz & DX", "Karl Storz & DX"),
             ("Kimadia", "Kimadia"),
             ("KRG", "KRG"),
             ("Legal", "Legal"),
             ("Medifa Maquet H&M", "Medifa Maquet h&M"),
             ("Mindray", "Mindray"),
             ("Modalities", "Modalities"),
             ("North", "North"),
             ("Packaging projects", "Packaging projects"),
             ("Reception", "Reception"),
             ("Resources", "Resources"),
             ("Siemens Lab", "Siemens Lab"),
             ("Siemens Radiology", "Siemens Radiology"),
             ("Siemens US", "Siemens US"),
             ("Social Marketing & Marcom", "Social Marketing $ Marcom"),
             ("South", "South"),
             ("Support Centre", "Support Centre"),
             ("Technicians", "Technicians"),
             ("Training", "Training")]

    divisions = fields.Selection(DIVISIONS, string="Old Division")
    units = fields.Selection(UNITS, string="Old Unit")
    budget_deputy = fields.Many2one('hr.employee', string="Budget Deputy")
    timeoff_deputy = fields.Many2one('hr.employee', string="Timeoff Deputy")

    @api.model
    def create(self, vals):
        res = super(HrEmployeeExtend, self).create(vals)
        unified_card_nationality = res.mapped('unified_card_nationality')
        family_ids = res.mapped('family_ids')
        family_passports = res.mapped('family_passports')
        unified_card_nationality.write({
            'res_id': res.id,
        })
        family_ids.write({
            'res_id': res.id,
        })
        family_passports.write({
            'res_id': res.id,
        })
        return res

    @api.constrains('budget_deputy')
    def on_save_budget_deputy(self):
        groups = self.user_id.groups_id
        access_ids = self.user_id.groups_id.model_access.filtered(lambda
                                                                      l: l.model_id.model == 'budget.analytic' or l.model_id.model == 'budget.line' or l.model_id.model == 'hr.expense' or l.model_id.model == 'hr.expense.sheet')
        rules = self.user_id.groups_id.rule_groups.filtered(lambda
                                                                l: l.model_id.model == 'budget.analytic' or l.model_id.model == 'budget.line' or l.model_id.model == 'hr.expense' or l.model_id.model == 'hr.expense.sheet')
        for access in access_ids:
            self.budget_deputy.user_id.groups_id.model_access = [(4, access.id)]
        for rule in rules:
            self.budget_deputy.user_id.groups_id.rule_groups = [(4, rule.id)]
        for group in groups:
            # if group.category_id.name == 'Expenses':
            self.budget_deputy.user_id.groups_id = [(4, group.id)]

    @api.constrains('timeoff_deputy')
    def on_save_timeoff_deputy(self):
        access_ids = self.user_id.groups_id.model_access.filtered(lambda
                                                                      l: l.model_id.model == 'hr.leave' or l.model_id.model == 'hr.leave.allocation' or l.model_id.model == 'hr.leave.type' or l.model_id.model == 'hr.leave.report.calendar')
        rules = self.user_id.groups_id.rule_groups.filtered(lambda
                                                                l: l.model_id.model == 'hr.leave' or l.model_id.model == 'hr.leave.allocation' or l.model_id.model == 'hr.leave.type' or l.model_id.model == 'hr.leave.report.calendar')
        for access in access_ids:
            self.timeoff_deputy.user_id.groups_id.model_access = [
                (4, access.id)]
        for rule in rules:
            self.timeoff_deputy.user_id.groups_id.rule_groups = [(4, rule.id)]
        for group in self.user_id.groups_id:
            self.timeoff_deputy.user_id.groups_id = [(4, group.id)]

    def _get_remaining_leaves(self):
        """ Helper to compute the remaining leaves for the current employees
            :returns dict where the key is the employee id, and the value is the remain leaves
        """
        start_date = fields.Datetime.now().date().replace(month=1, day=1)
        end_date = fields.Datetime.now().date().replace(month=12, day=31)
        self._cr.execute("""
            SELECT
                sum(h.number_of_days) AS days,
                h.employee_id
            FROM
                (
                    SELECT holiday_status_id, number_of_days,
                        state, employee_id ,date_from,date_to
                    FROM hr_leave_allocation
                    UNION ALL
                    SELECT holiday_status_id, (number_of_days * -1) as number_of_days,
                        state, employee_id ,date_from,date_to
                    FROM hr_leave where date_from >= %s AND date_to <= %s
                ) h
                join hr_leave_type s ON (s.id=h.holiday_status_id )
            WHERE
                s.active = true AND h.state='validate' AND 
                (s.allocation_type='regular') AND
                h.employee_id in %s
            GROUP BY h.employee_id""", (start_date, end_date, tuple(self.ids),))
        return dict((row['employee_id'], row['days']) for row in
                    self._cr.dictfetchall())

    def action_time_off_dashboard(self):
        """Overwrite the function to view the leave report instead of leaves"""
        return {
            'name': _('Time Off Dashboard'),
            'type': 'ir.actions.act_window',
            'res_model': 'hr.leave',
            'views': [(self.env.ref('hr_holidays.hr_leave_view_kanban').id, 'kanban'),
                    (self.env.ref('hr_holidays.hr_leave_view_tree').id, 'list'),
                    (self.env.ref('hr_holidays.hr_leave_view_dashboard').id, 'calendar'),
                    (self.env.ref('hr_holidays.hr_leave_view_form').id, 'form')],
            'domain': [('employee_id', 'in', self.ids)],
            'context': {
                'employee_id': self.ids,
                'search_default_year': 1,
                'search_default_group_type': 1
            },
        }

    def _compute_allocation_count(self):
        for employee in self:
            day = fields.datetime.now()
            start_date = day.replace(month=1, day=1)
            end_date = day.replace(month=12, day=31).date()
            allocations = self.env['hr.leave.allocation'].search([
                ('employee_id', '=', employee.id),
                ('holiday_status_id.active', '=', True),
                ('state', '=', 'validate'), ('create_date', '>=', start_date),
                ('create_date', '<=', end_date)
            ])
            employee.allocation_count = float_round(
                sum(allocations.mapped('number_of_days')), precision_digits=2)
            employee.allocation_display = "%g" % employee.allocation_count

    def compute_is_set_division_and_unit_visible(self):
        for rec in self:
            if rec.divisions:
                if not rec.new_divisions:
                    rec.is_set_division_and_unit_visible = True
                else:
                    rec.is_set_division_and_unit_visible = False
            else:
                rec.is_set_division_and_unit_visible = False

            if rec.units:
                if not rec.new_units:
                    rec.is_set_division_and_unit_visible = True
                else:
                    rec.is_set_division_and_unit_visible = False
            else:
                rec.is_set_division_and_unit_visible = False

    def set_divisions_and_units(self):
        obj = self.env['hr.employee'].search(
            ['|', ('divisions', '!=', False), ('units', '!=', False)])
        for rec in obj:
            if rec.divisions:
                div_obj = self.env['division.division'].search(
                    [('name', '=', rec.divisions)])
                if div_obj:
                    rec.new_divisions = div_obj.id
                else:
                    divv_obj = self.env['division.division'].create({
                        'name': rec.divisions,
                    })
                    rec.new_divisions = divv_obj.id

            if rec.units:
                unit_obj = self.env['unit.unit'].search(
                    [('name', '=', rec.units)])
                if unit_obj:
                    rec.new_units = unit_obj.id
                else:
                    unit_obj = self.env['unit.unit'].create({
                        'name': rec.units,
                    })
                    rec.new_units = unit_obj.id


class PublicEmployeeInherit(models.Model):
    _inherit = 'hr.employee.public'

    new_divisions = fields.Many2one('division.division', string="Division new")
    new_units = fields.Many2one('unit.unit', string="Units")
    budget_deputy = fields.Many2one('hr.employee.public',
                                    string="Budget Deputy")
    timeoff_deputy = fields.Many2one('hr.employee.public',
                                     string="Timeoff Deputy")
