from odoo import fields, models, api


class Equipments(models.Model):
    _name = 'equipment.equipment'
    _description = 'Equipments'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string="Equipment Name", tracking=True)
    purchase_date = fields.Date(string="Purchase Date", tracking=True)
    attachment_ids = fields.Many2many('ir.attachment',string="Attachment", tracking=True)
    equipment_type_id = fields.Many2one('equipment.type', string="Equipment Type", tracking=True)
    equipment_status_id = fields.Many2one('equipment.status', string="Equipment Status", tracking=True)
    equipment_condition_id = fields.Many2one('equipment.condition', string="Equipment Condition", tracking=True)
    serial_number = fields.Char(string="Serial Number", tracking=True)
    notes = fields.Text(string="Notes", tracking=True)
    employee_history_ids = fields.One2many('equipment.employee.history', 'equipment_id', string="Employee History", tracking=True)
    is_equipment_available = fields.Boolean(compute='compute_is_equipment_available', store=True, default=True)
    tool_line_ids = fields.One2many('equipment.tools.line', 'equipment_id', string="Tools")

    employee_name_search = fields.Char(string="Employee Search",
                                       compute='_compute_employee_name_search',
                                       store=True, index=True)

    @api.model
    def create(self, vals):
        res = super(Equipments, self).create(vals)
        attachment_ids = res.mapped('attachment_ids')
        attachment_ids.write({
            'res_id': res.id,
        })
        return res

    @api.depends('employee_history_ids.employee_id.name')
    def _compute_employee_name_search(self):
        for rec in self:
            names = rec.employee_history_ids.mapped('employee_id.name')
            rec.employee_name_search = ', '.join(filter(None, names))


    @api.depends('employee_history_ids')
    def compute_is_equipment_available(self):
        for rec in self:
            if rec.employee_history_ids:
                for history in rec.employee_history_ids:
                    if not history.return_date:
                        rec.is_equipment_available = False
                    else:
                        rec.is_equipment_available = True
            else:
                rec.is_equipment_available = True
# TODO: Advanced filter option is available in odoo 13 so the FIlter_menu.js file is not required
    def get_filter_records(self, employee_name):
        employee_history = self.env['equipment.employee.history'].search(
            [('employee_id.name', 'ilike', employee_name)]).mapped('equipment_id.id')
        return list(set(employee_history))

    def get_current_acquirer_filter_records(self, employee_name):
        employee_history = self.env['equipment.employee.history'].search(
            [('employee_id.name', 'ilike', employee_name), ('return_date', '=', False)]).mapped(
            'equipment_id.id')
        return list(set(employee_history))

    def get_previous_acquirer_filter_records(self, employee_name):
        employee_history = self.env['equipment.employee.history'].search(
            [('employee_id.name', 'ilike', employee_name), ('return_date', '!=', False)]).mapped(
            'equipment_id.id')
        return list(set(employee_history))
