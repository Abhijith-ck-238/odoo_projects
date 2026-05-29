import datetime
from dateutil.relativedelta import relativedelta
from odoo import models, fields, _, api
from odoo.exceptions import UserError
from odoo.models import NewId


class ContractContractExtend(models.Model):
    """ Inherited contract """
    _inherit = 'contract.contract'
    _description = 'contract'

    active = fields.Boolean(default=True)
    name = fields.Char(string="Name", compute='_gen_name',
                       search='_name_search')
    is_technical_products_only = fields.Boolean(
        string="Show Technical Products only", default=False)
    financial_docs1 = fields.Binary(string="Financial Document 1")
    financial_docs2 = fields.Binary(string="Financial Document 2")
    pm_interval = fields.Many2one('interval.interval', string="PM Interval")
    comp_id = fields.Many2one('company.company', string="Company")
    dx_financial_documents = fields.Many2many(comodel_name="ir.attachment",
                                              relation="attachement_contract_dx_financial_document_rel",
                                              column1="contract_id",
                                              column2="attachment_id",
                                              string="DX Financial Documents",
                                              groups="purchase.group_purchase_user")
    old_data = fields.Boolean(default=True)
    product_show_option = fields.Char(compute='compute_product_show_option')
    is_eoc = fields.Boolean(compute='compute_is_eoc', store=True)

    is_contract_in_warranty = fields.Boolean(string="Contract in warranty")
    pm_count = fields.Integer(string='PM Count', compute='_compute_pm',
                              readonly=True)
    pm_ids = fields.Many2many("preventive.maintainence", string='PM Tickets',
                              compute="_compute_pm", readonly=True,
                              copy=False)
    helpdesk_count = fields.Integer(string='Helpdesk ticket Count',
                                    compute='_compute_helpdesk_tickets',
                                    readonly=True)
    pm_ticket_count = fields.Integer(string='Helpdesk ticket Count',
                                    compute='_compute_pm_ticket_count',
                                    readonly=True)
    helpdesk_ticket_ids = fields.Many2many("helpdesk.tickets",
                                           string='Helpdesk tickets',
                                           compute="_compute_helpdesk_tickets",
                                           readonly=True,
                                           copy=False)
    pac_document_count = fields.Integer(compute='_compute_pac_document_count')
    dac_document_count = fields.Integer(compute='_compute_dac_document_count')
    handing_over_document_count = fields.Integer(compute='_compute_handing_over_document_count')
    related_shipment_count = fields.Integer(compute="_compute_related_shipment_count")
    training_ticket_count = fields.Integer(compute="_compute_training_ticket_count", store=True)
    lc_activated = fields.Date(string="L/C Activated")

    def write(self, vals):
        if vals.get('lc_activated'):
            ticket =self.env['training.ticket'].create({
                'contract_id': self.id
            })
            if ticket:
                users = self.env.ref(
                    "custom_training.group_training_officer").users
                for user in users:
                    self.env['mail.activity'].sudo().create({
                        'display_name': 'Training Ticket Created',
                        'summary': 'Training Ticket Created',
                        'note': 'Training ticket ' + ticket.name + ' is created from the contract ' +self.name+ '.',
                        'date_deadline': fields.datetime.now(),
                        'user_id': int(user.id),
                        'res_id': ticket.id,
                        'res_model_id': self.env['ir.model'].sudo().search(
                            [('model', '=', 'training.ticket')],
                            limit=1).id,
                        'activity_type_id': self.env.ref('custom_training.mail_activity_training_notify_user').id,
                    })
        return super(ContractContractExtend,self).write(vals)

    @api.depends('lc_activated')
    def _compute_training_ticket_count(self):
        for rec in self:
            tickets = self.env['training.ticket'].search([("contract_id", "=", rec.id)])
            rec.training_ticket_count = len(tickets)


    def _compute_related_shipment_count(self):
        for rec in self:
            rec.related_shipment_count = self.env['logistics.shipment'].search_count(
                [("contract_ids", "in", rec.id)])


    @api.depends('product_lines.pac_document')
    def _compute_pac_document_count(self):
        document_ids = []
        for rec in self.product_lines:
            document_ids += rec.pac_document.ids
            name = "PAC of "
            if rec.product_char:
                name += rec.product_char + " - "
            if rec.site:
                name += rec.site.site_name + " - "
            if rec.province:
                name += rec.province.name + " - "
            if rec.sn:
                name += "#" + rec.sn + " - "
            if rec.contract_id:
                if rec.contract_id.number:
                    name += rec.contract_id.number
            rec.pac_document.write({
                'public': True,
                'name': name
            })
        self.pac_document_count = len(document_ids)

    @api.depends('product_lines.dac_document')
    def _compute_dac_document_count(self):
        document_ids = []
        for rec in self.product_lines:
            document_ids += rec.dac_document.ids
            name = "DAC of "
            if rec.product_char:
                name += rec.product_char + " - "
            if rec.site:
                name += rec.site.site_name + " - "
            if rec.province:
                name += rec.province.name + " - "
            if rec.sn:
                name += "#" + rec.sn + " - "
            if rec.contract_id:
                if rec.contract_id.number:
                    name += rec.contract_id.number
            rec.dac_document.write({
                'public': True,
                'name': name
            })
        self.dac_document_count = len(document_ids)

    @api.depends('product_lines.handing_over_document')
    def _compute_handing_over_document_count(self):
        document_ids = []
        for rec in self.product_lines:
            document_ids += rec.handing_over_document.ids
            name = "Handing Over of "
            if rec.product_char:
                name += rec.product_char + " - "
            if rec.site:
                name += rec.site.site_name + " - "
            if rec.province:
                name += rec.province.name + " - "
            if rec.sn:
                name += "#" + rec.sn + " - "
            if rec.contract_id:
                if rec.contract_id.number:
                    name += rec.contract_id.number
            rec.handing_over_document.write({
                'public': True,
                'name': name
            })
        self.handing_over_document_count = len(document_ids)

    def action_related_shipment(self):
        """ Return action for pac document."""
        return {
            "type": "ir.actions.act_window",
            "res_model": "logistics.shipment",
            "views": [[False,"list"],
                      [False, "form"]],
            "domain": [("contract_ids", "in", self.id)],
            "context": dict(self._context, create=False),
            "name": "Shipment",
        }

    def action_pac_document(self):
        """ Return action for pac document."""
        document_ids = []
        for rec in self.product_lines:
            document_ids += rec.pac_document.ids
        return {
            "type": "ir.actions.act_window",
            "res_model": "ir.attachment",
            "views": [[False, "kanban"],
                      [False,"form"],
                      [False, "list"]],
            "domain": [("id", "in", document_ids)],
            "context": dict(self._context, create=False),
            "name": "PAC",
        }

    def action_dac_document(self):
        """ Return action for dac document."""
        document_ids = []
        for rec in self.product_lines:
            document_ids += rec.dac_document.ids
        return {
            "type": "ir.actions.act_window",
            "res_model": "ir.attachment",
            "views": [[False, "kanban"],
                      [False,"form"],
                      [False, "list"]],
            "domain": [("id", "in", document_ids)],
            "context": dict(self._context, create=False),
            "name": "DAC",
        }

    def action_handing_over_document(self):
        """ Return action for handing over document."""
        document_ids = []
        for rec in self.product_lines:
            document_ids += rec.handing_over_document.ids
        return {
            "type": "ir.actions.act_window",
            "res_model": "ir.attachment",
            "views": [[False, "kanban"],
                      [False,"form"],
                      [False, "list"]],
            "domain": [("id", "in", document_ids)],
            "context": dict(self._context, create=False),
            "name": "Handing Over Document",
        }

    def action_training_tickets(self):
        return {
            "type": "ir.actions.act_window",
            "res_model": "training.ticket",
            "views": [[False, "kanban"],
                      [False, "form"],
                      [False, "list"]],
            "domain": [("contract_id", "=", self.id)],
            "context": dict(self._context, create=False),
            "name": "Training Ticket",
        }


    def _compute_pm(self):
        """ Method to find all related preventive maintenances and its count."""
        for rec in self:
            pm_ids = self.env['preventive.maintainence'].search(
                [('contract_id', '=', rec.id)])
            rec.pm_ids = pm_ids.ids
            rec.pm_count = len(rec.pm_ids)

    def _compute_helpdesk_tickets(self):
        """ Method to find all related helpdesk tickets and its count."""
        for rec in self:
            helpdesk_tickets = self.env['helpdesk.ticket'].search(
                ['|', ('pm_id.contract_id', '=', self.id),
                 ('contract_id', '=', self.id)])
            rec.helpdesk_ticket_ids = helpdesk_tickets.ids
            rec.helpdesk_count = len(rec.helpdesk_ticket_ids)


    def _compute_pm_ticket_count(self):
        """ Method to find all related helpdesk tickets and its count."""
        for rec in self:
            helpdesk_tickets = self.env['helpdesk.ticket'].search(
                [('ticket_type_id', '=', 5),
                 ('contract_id', '=', self.id)])
            rec.pm_ticket_count = len(helpdesk_tickets)

    def button_view_related_pm_tickets(self):
        """ Method to view the related helpdesk tickets. """

        return {
            'name': "Helpdesk Tickets",
            'type': 'ir.actions.act_window',
            'views': [(self.env.ref('helpdesk.helpdesk_ticket_view_kanban').id,
                       'kanban'), (False, 'form')],
            'view_mode': 'list',
            'res_model': 'helpdesk.ticket',
            'target': 'current',
            'domain': [('id', 'in', self.helpdesk_ticket_ids.ids)],
        }

    def button_view_related_pm(self):
        """ Method to view the related preventive maintenances. """
        return {
            'name': "Preventive Maintenance",
            'type': 'ir.actions.act_window',
            'views': [(self.env.ref('itkan_pm.preventive_maintainence_tree').id,
                       'list'), (False, 'form')],
            'view_mode': 'list',
            'res_model': 'preventive.maintainence',
            'target': 'current',
            'domain': [('id', 'in', self.pm_ids.ids)],
        }

    def button_view_related_pm_ticket(self):
        """ Method to view the related helpdesk. """
        return {
            'name': "Helpdesk",
            'type': 'ir.actions.act_window',
            'views': [(self.env.ref('helpdesk.helpdesk_ticket_view_kanban').id,
                       'kanban'), (False, 'form')],
            'view_mode': 'list',
            'res_model': 'helpdesk.ticket',
            'target': 'current',
            'domain': [('ticket_type_id', '=', 5),('id', 'in', self.helpdesk_ticket_ids.ids)],
        }

    def compute_contract_in_warranty(self):
        """ Method to compute contract in warranty or not."""
        contracts = self.env['contract.contract'].search([])
        for contract in contracts:
            for rec in contract.product_lines:
                starting_date = rec.starting_date
                if starting_date:
                    if rec.warranty:
                        warranty_date = starting_date + relativedelta(
                            years=rec.warranty)
                        if warranty_date <= datetime.date.today():
                            rec.is_contract_in_warranty = False
                        else:
                            contract.is_contract_in_warranty = True
                            break
                    if rec.maintainence:
                        maintainence_date = starting_date + relativedelta(
                            years=rec.maintainence)
                        if maintainence_date >= datetime.date.today():
                            rec.is_active_maintenance = True

    def create_pm_schedule(self):
        """ method to create preventive maintenance manually from contract."""
        if not self.pm_created and self.pm_interval:
            for line in self.product_lines:
                pmid = self.env['preventive.maintainence'].search(
                    [('sn', '=ilike', line.sn)])
                if pmid:
                    pass
                else:
                    if line.sn:
                        pm_id = self.env['preventive.maintainence'].create({
                            'sn': line.sn,
                            'iq': line.contract_id.iq,
                            'interval': str(self.pm_interval.value),
                            'total_no_of_years': line.warranty + line.maintainence,
                            'contract_id': line.contract_id.id,
                            'contract_product_id': line.id,
                        })
                        pm_id.search_sn()

    def set_is_eoc(self):
        """ Scheduled action to set is_eoc"""
        today_date = fields.Date.today()
        contract = self.env['contract.contract'].search([])
        for rec in contract:
            rec.is_eoc = any(line.eoc_date and line.eoc_date >= today_date for line in rec.product_lines)


    @api.depends('product_lines.starting_date')
    def compute_is_eoc(self):
        """ method to compute is_eoc."""
        for rec in self:
            if rec.product_lines:
                for product_line in rec.product_lines:
                    if product_line.eoc_date:
                        today_date = fields.Date.today()
                        if product_line.eoc_date >= today_date:
                            rec.is_eoc = True
                            break
                        else:
                            rec.is_eoc = False
                    else:
                        rec.is_eoc = False
            else:
                rec.is_eoc = False

    def compute_product_show_option(self):
        """ method to compute product_show_option"""
        for rec in self:
            rec.product_show_option = self.env.user.employee_id.department_id.product_show_option

    @api.depends('iq', 'number', 'partner_id')
    def _gen_name(self):
        """ Method to generate names."""
        for contract in self:
            name = ""
            if contract.number:
                name += contract.number
            else:
                if contract.iq:
                    name += contract.iq
                    contract.name = name
                    continue

            name += f" - {contract.iq}"
            name += f" - {contract.partner_id.name}"
            contract.name = name

    def _name_search(self, operator, value):
        """ Method to search for name."""
        contracts = self.env['contract.contract'].search([])

        def safe_get_name(rec):
            try:
                return rec.name and rec.name.lower()
            except Exception:
                return ''

        value_lower = value.lower() if value else ''

        if operator == 'ilike':
            res = contracts.filtered(
                lambda rec: value_lower in safe_get_name(rec))
        elif operator == 'not ilike':
            res = contracts.filtered(
                lambda rec: value_lower not in safe_get_name(rec))
        elif operator == '=':
            res = contracts.filtered(
                lambda rec: value_lower == safe_get_name(rec))
        elif operator == '!=':
            res = contracts.filtered(
                lambda rec: value_lower != safe_get_name(rec))
        else:
            res = self.env['contract.contract']

        return [('id', 'in', res.ids)]

    

    def generated_pm_records(self):
        """Method to automatically create preventive maintenance from contract
        lines."""
        contracts = self.env['contract.contract'].search(
            [('pm_interval', '!=', False)])
        modalities = self.env['ir.config_parameter'].sudo().get_param(
            'custom_helpdesk.modality_ids')
        modality = modalities.translate(
            {ord(c): None for c in "[]"})
        li = list(modality.split(","))
        modality_list = []
        for rec in li:
            modality_list.append((int(rec)))

        for contract_id in contracts:
            for contract_line_id in contract_id.product_lines.filtered(
                    lambda x: not x.pm_id and x.eoc_date and x.starting_date and  x.eoc_date > x.starting_date and x.sn != False):
                new_values = {
                    'sn': contract_line_id.sn,
                    'ref': 'eoc',
                    'interval': str(
                        contract_id.pm_interval.value) if contract_id.pm_interval else False,
                    'total_no_of_years': contract_line_id.warranty + contract_line_id.maintainence,
                    'contract_id': contract_line_id.contract_id.id,
                    'contract_product_id': contract_line_id.id,
                }

                pm_id = self.env['preventive.maintainence'].create(new_values)
                pm_id.search_sn()
                pm_id.generate_dates_table()
                if pm_id.modality.id in modality_list:
                    pm_id.set_active()
                contract_line_id.pm_id = pm_id.id
            if not contract_id.pm_created:
                contract_id.pm_created = True

    def action_remove_product_lines(self):
        """ Method to remove product lines."""
        for rec in self:
            rec.product_lines.unlink()


class ContractProductExtend(models.Model):
    """ Inherited Contract Product"""
    _inherit = 'contract.product'
    _order = "sub_item_sequence asc"

    config = fields.Many2one('offering.config', string="Config")
    province = fields.Many2one('contract.province', string="Province",
                               compute='compute_hd_and_province', store=True,
                               readonly=False)
    functional_location = fields.Char(string="Functional Location",
                                      compute='calc_functional_location',
                                      store=True)
    eoc_date = fields.Date(string="EOC Date", compute='compute_eoc_date', store=True)
    peripherals = fields.Many2many('peripheral.peripheral',
                                   relation="peripheral_contract_product_rel",
                                   column1="contract_id",
                                   column2="peripheral_id",
                                   string="Peripherals")
    notes = fields.Text(string="Notes")
    technical_product = fields.Many2one('technical.product',
                                        domain="[('is_technical_product', '=', True)] ",
                                        string="Technical Product")
    hd_name = fields.Many2one('health.department', string="DOH",
                              compute='compute_hd_and_province', store=True,
                              readonly=False)
    site = fields.Many2one("contract.site", string="Site")
    is_contract_in_warranty = fields.Boolean(
        compute='_compute_is_contract_in_warranty',
        search='_search_contract_in_warranty',
        store=True)
    is_active_maintenance = fields.Boolean()
    parent_product_id = fields.Many2one('contract.product',
                                        string="Parent Product")
    sub_item_sequence = fields.Float(string="Sub item Sequence",
                                     compute='compute_sub_item_sequence',
                                     store=True)
    active_contract = fields.Boolean(string="Active Contract",
                                     compute='compute_active_contract',
                                     search='_search_active_contract')

    pac_document = fields.Many2many('ir.attachment', string='PAC',
                                    relation="attachment_contract_line_pac_document_rel",
                                    column1="contract_line_id",
                                   column2="attachment_id",
                                   attachment=True)
    dac_document =fields.Many2many('ir.attachment', string='DAC',
                                   relation = "attachment_contract_line_dac_document_rel",
                                   column1 = "contract_line_id",
                                   column2 = "attachment_id")
    handing_over_document = fields.Many2many('ir.attachment', string='Handing Over Documents',
                                            relation="attachment_contract_line_handing_over_document_rel",
                                            column1="contract_line_id",
                                            column2="attachment_id")
    contract_type = fields.Selection(selection_add=[("installation_only", "Installation Only")], string="Contract Type")
    
    @api.model
    def create(self, vals):
        res = super(ContractProductExtend, self).create(vals)
        pac_document = res.mapped('pac_document')
        dac_document = res.mapped('dac_document')
        handing_over_document = res.mapped('handing_over_document')
        pac_document.write({
            'res_id': res.id,
        })
        dac_document.write({
            'res_id': res.id,
        })
        handing_over_document.write({
            'res_id': res.id,
        })
        return res

    @api.depends('site')
    def compute_hd_and_province(self):
        for rec in self:
            rec.hd_name = rec.site.doh_id
            rec.province =  rec.site.site_province

    @api.depends('contract_id.active')
    def compute_active_contract(self):
        for rec in self:
            if rec.contract_id:
                if rec.contract_id.active:
                    rec.active_contract = True
                else:
                    rec.active_contract = False
            else:
                rec.active_contract = True

    @api.model
    def _search_active_contract(self, operator, value):
        """Method for searching the contract is in warranty or not."""
        if operator == '=':
            recs = self.search([]).filtered(
                lambda x: x.active_contract is True )
            if recs:
                return [('id', 'in', [x.id for x in recs])]
        else:
            recs = self.search([]).filtered(
                lambda x: x.active_contract is False)
            if recs:
                return [('id', 'in', [x.id for x in recs])]

    @api.depends('parent_product_id')
    def compute_sub_item_sequence(self):
        for rec in self:
            if rec:
                if isinstance(rec.id, NewId):
                    rec.sub_item_sequence = False
                else:
                    if rec.parent_product_id:
                        contract_product_ids = self.env[
                            'contract.product'].search([
                            ('parent_product_id', '=',
                             rec.parent_product_id.id)])
                        i = 0.1
                        for line in contract_product_ids:
                            seq = line.parent_product_id.id + i
                            line.sub_item_sequence = seq
                            i += 0.1
                        rec.parent_product_id.sub_item_sequence = rec.parent_product_id.id
                    else:
                        rec.sub_item_sequence = False

    def _compute_name(self):
        """ Method to compute name of contract product line."""
        for rcd in self:
            if rcd.product_char:
                rcd.name = rcd.product_char
            else:
                rcd.name = rcd.product_id.display_name or "Empty"

            if rcd.sn:
                rcd.name += ' - ' + rcd.sn

    @api.model
    def _search_contract_in_warranty(self, operator, value):
        """Method for searching the contract is in warranty or not."""
        if operator == '=':
            recs = self.search([]).filtered(
                lambda x: x.is_contract_in_warranty is True)
            if recs:
                return [('id', 'in', [x.id for x in recs])]
        else:
            recs = self.search([]).filtered(
                lambda x: x.is_contract_in_warranty is False)
            if recs:
                return [('id', 'in', [x.id for x in recs])]

    @api.depends('contract_id')
    def _compute_is_contract_in_warranty(self):
        """ Method to check the contract is in warranty or not."""
        for rec in self:
            starting_date = rec.starting_date
            if starting_date:
                if rec.warranty:
                    warranty_date = starting_date + relativedelta(
                        years=rec.warranty)
                    if warranty_date <= datetime.date.today():
                        rec.is_contract_in_warranty = False
                    else:
                        rec.is_contract_in_warranty = True
                else:
                    rec.is_contract_in_warranty = False
            else:
                rec.is_contract_in_warranty = False

    @api.onchange('technical_product')
    def onchange_technical_product(self):
        """ Method to give values to modality,supplier and product char when
        technical product is changed. """
        self.product_char = self.technical_product.name
        self.modality = self.technical_product.modality.id
        self.supplier = self.technical_product.partner_id.id

    def add_sub_line(self):
        """ Method to add sub line for contract product main items"""
        sub_contract_product_ids = self.env['contract.product'].search(
            [('parent_product_id', '=', self.id)])
        sub_lines = []
        for rec in sub_contract_product_ids:
            sub_lines.append((0, 0, {
                "product_char": rec.product_char,
                "product_id": rec.product_id.id,
                "price": rec.price,
                "qty": rec.qty,
                "site_id": rec.site.id,
                "province_id": rec.province.id,
                "health_department_id": rec.hd_name.id,
                "functional_location": rec.functional_location,
                "partner_id": rec.supplier.id,
                "modality_id": rec.modality.id,
                "serial_no": rec.sn,
                "warranty": rec.warranty,
                "maintenance": rec.maintainence,
                "peripherals": rec.peripherals.ids,
                "starting_date": rec.starting_date,
                "pac_date": rec.pac_date,
                "eoc_date": rec.eoc_date,
                "contract_type": rec.contract_type,
                "notes": rec.notes,
                "config": rec.config.id,
                "password_validity": rec.password_validity,
                "password_validity_date": rec.password_validity_date,
                "parent_product_id": rec.parent_product_id.id,
                "part_number": rec.part_number,
                "technical_product": rec.technical_product.id,
            }))

        return {
            'name': "Add Sub lines",
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'contract.sub.line.wizard',
            'view_id': self.env.ref(
                'custom_contract.contract_sub_line_wizard_view').id,
            'target': 'current',
            'context': {'default_contract_product_id': self.id,
                        'default_contract_sub_lines': sub_lines,
                        },

        }

    def choose_peripherals(self):
        """ Method to show a wizard to choose peripherals. """
        return {
            'name': "Choose Peripherals",
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'peripherals.wizard',
            'view_id': self.env.ref(
                'custom_contract.peripheral_wizard_view').id,
            'target': 'new',
            'context': {'default_contract_product_id': self.id},

        }

    @api.depends('starting_date', 'warranty', 'maintainence')
    def compute_eoc_date(self):
        """ Method to compute eoc date. """
        for item in self:
            start_date = item.starting_date
            warrenty = item.warranty
            if start_date:
                yr = start_date.year
                maintenance = item.maintainence
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

    @api.onchange('province')
    def onchange_province(self):
        """ Method to return domain for site when the province is changed. """
        if self.province:
            return {
                'domain': {'site': [('site_province', '=', self.province.id)]}}
        else:
            pass

    @api.onchange('product_id')
    def onchange_product_id(self):
        """ Method to give values to modality,supplier and product char when
        product is changed. """
        for rec in self:
            rec.modality = rec.product_id.modality.id
            rec.supplier = rec.product_id.partner_id.id
            rec.product_char = rec.product_id.name

    @api.depends("site")
    def calc_functional_location(self):
        """ FL = 13 digit = Province number + Digits(Zeros) + Site number """
        for item in self:
            if item.site:
                prov_num = str(item.site.site_province.prov_number)
                site_num = str(item.site.site_number)
                zeros_num = 8
                item.functional_location = prov_num + (
                        "0" * zeros_num) + site_num
            else:
                item.functional_location = False

    @api.onchange('product_id')
    def onchange_product_lines(self):
        """ Method to return domain to product id."""
        if self.contract_id.is_technical_products_only:
            return {
                'domain': {'product_id': [('is_technical_product', '=', True)]}}
        else:
            pass

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

    def get_filter_records(self):
        serial_number = self.env['contract.product'].search([('eoc_date','>=', fields.Date.today())]).mapped('sn')
        records = self.env['contract.product'].search([('eoc_date','<', fields.Date.today()), ('sn', 'not in', serial_number)]).mapped('id')
        return list(set(records))

class CustomPreventiveMaintanence(models.Model):
    """ Class inherits Preventive Maintenance"""
    _inherit = 'preventive.maintainence'
    province = fields.Many2one('contract.province', string="Province",
                               related='contract_product_id.province')
