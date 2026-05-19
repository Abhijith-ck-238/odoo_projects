from odoo import models, fields, api, _
from odoo.exceptions import UserError


class ContractSubLineWizard(models.TransientModel):
    _name = "contract.sub.line.wizard"
    _description = 'Contract sub line wizard'

    contract_product_id = fields.Many2one('contract.product')
    contract_sub_lines = fields.One2many('contract.sub.line.wizard.line',
                                         "conn", string='Sub lines')

    def save_sub_lines(self):
        sub_lines = []
        for rec in self.contract_sub_lines:
            if rec.parent_product_id:
                pass
            else:
                sub_lines.append((0, 0, {
                    "product_char": rec.product_char,
                    "product_id": rec.product_id.id,
                    "price": rec.price,
                    "qty": rec.qty,
                    "site": rec.site_id.id,
                    "province": rec.province_id.id,
                    "hd_name": rec.health_department_id.id,
                    "functional_location": rec.functional_location,
                    "supplier": rec.partner_id.id,
                    "modality": rec.modality_id.id,
                    "sn": rec.serial_no,
                    "warranty": rec.warranty,
                    "maintainence": rec.maintenance,
                    "peripherals": rec.peripherals.ids,
                    "starting_date": rec.starting_date,
                    "pac_date": rec.pac_date,
                    "eoc_date": rec.eoc_date,
                    "contract_type": rec.contract_type,
                    "notes": rec.notes,
                    "config": rec.config.id,
                    "password_validity": rec.password_validity,
                    "password_validity_date": rec.password_validity_date,
                    "parent_product_id": self.contract_product_id.id,
                    "part_number": rec.part_number,
                    "technical_product": rec.technical_product.id,
                }))
        self.contract_product_id.contract_id.product_lines = sub_lines
        return {
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'contract.contract',
            'view_id': self.env.ref('contracts.form').id,
            'target': 'current',
            'res_id': self.contract_product_id.contract_id.id,

        }


class ContractSubLineWizardLine(models.TransientModel):
    _name = "contract.sub.line.wizard.line"
    _description = 'Contract sub line wizard line'

    CONTRACT_TYPES = [("Supplying & Maintenance", "Supplying & Maintenance"),
                      ("Maintenance", "Maintenance"),
                      ("Supplying", "Supplying"),
                      ("3rd party", "3rd party"), ("Demo", "Demo"),
                      ("N.A", "N.A"), ("Other", "Other")]

    name = fields.Char(string="name", compute="_compute_name")
    product_char = fields.Char(string="Product Char")
    conn = fields.Many2one('contract.sub.line.wizard')
    product_id = fields.Many2one('product.product', string="Product")
    price = fields.Float(string="Price")
    qty = fields.Integer(string="Quantity")
    site_id = fields.Many2one('contract.site', string="Site",
                              domain="[('site_province','=',province_id)]")
    province_id = fields.Many2one('contract.province', string="Province")
    health_department_id = fields.Many2one('health.department',
                                           string="Health Department")
    functional_location = fields.Char(string="Functional Location")
    partner_id = fields.Many2one('res.partner', string="Vendor")
    modality_id = fields.Many2one('contract.modality', string="Modality")
    serial_no = fields.Char(string="Serial No")
    warranty = fields.Integer(string="Warranty")
    maintenance = fields.Integer(string="Maintenance")
    peripherals = fields.Many2many('peripheral.peripheral')
    starting_date = fields.Date(string="Starting Date")
    pac_date = fields.Date(string="PAC Date")
    eoc_date = fields.Date(string="EOC Date", compute='compute_eoc_date')
    contract_type = fields.Selection(CONTRACT_TYPES, string="Contract Type")
    notes = fields.Text(string="Notes")
    config = fields.Many2one('offering.config', string="Config")
    password_validity = fields.Selection([("yes", "Yes"), ("no", "No")],
                                         string="Password/Validity")
    password_validity_date = fields.Date(string="Password Validity Date")
    part_number = fields.Char(string="Part Number")
    technical_product = fields.Many2one('product.product',
                                        domain="[('is_technical_product', '=', True)] ",
                                        string="Technical Product")
    is_technical_products_only = fields.Boolean(
        related='conn.contract_product_id.contract_id.is_technical_products_only')
    parent_product_id = fields.Many2one('contract.product',
                                        string="Parent Product")

    def action_display_sub_units(self):
        """ Method to display subunits."""
        if self.config:
            list_of_lines = []
            for line in self.config.product_bom_lines:
                list_of_lines.append(
                    (0, 0, {
                        "product_id": line.product_id.id,
                        "qty": line.qty
                    }))
            return {
                'name': "Config Window",
                'type': 'ir.actions.act_window',
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'config.wizard',
                'view_id': self.env.ref(
                    'custom_contract.config_wizard_view').id,
                'target': 'new',
                'context': {'default_config_id': self.config.id,
                            'default_product_lines': list_of_lines,
                            'default_description': self.config.product_id.name,
                            },
                'flags': {'form': {'action_buttons': False}, },
            }
        else:
            raise UserError(_("No config found"))

    @api.onchange('technical_product')
    def onchange_technical_product(self):
        self.product_char = self.technical_product.name
        self.modality_id = self.technical_product.modality.id
        self.partner_id = self.technical_product.partner_id.id

    @api.onchange('product_id')
    def onchange_product_id(self):
        self.product_char = self.product_id.name
        self.modality_id = self.product_id.modality.id
        self.partner_id = self.product_id.partner_id.id

    def _compute_name(self):
        """ Method to compute name of contract product line."""
        for rcd in self:
            if rcd.product_char:
                rcd.name = rcd.product_char
            else:
                rcd.name = rcd.product_id.display_name or "Empty"

            if rcd.serial_no:
                rcd.name += ' - ' + rcd.serial_no

    @api.depends('starting_date', 'warranty', 'maintenance')
    def compute_eoc_date(self):
        for item in self:
            start_date = item.starting_date
            warrenty = item.warranty
            if start_date:
                yr = start_date.year
                maintenance = item.maintenance
                yearnew = yr + maintenance + warrenty
                if (yr % 4 == 0 and yr % 100 != 0) or (yr % 400 == 0):
                    if (yearnew % 4 == 0 and yearnew % 100 != 0) or (
                            yearnew % 400 == 0):
                        new_date = start_date.replace(year=yearnew)
                    else:
                        if start_date.day == 29:
                            new_date = start_date.replace(year=yearnew, day=28)
                        else:
                            new_date = start_date.replace(year=yearnew)
                else:
                    new_date = start_date.replace(year=yearnew)
                item.eoc_date = new_date
            else:
                item.eoc_date = ''
