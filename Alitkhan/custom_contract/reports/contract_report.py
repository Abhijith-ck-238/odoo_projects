from odoo import fields, models
from odoo import tools

class ContractReport(models.Model):
    _name = "contract.report"
    _description = "Contract Analysis Report"
    _auto = False

    site = fields.Many2one('contract.site', string='Site')
    partner_id = fields.Many2one('res.partner', string="Vendor")
    modality = fields.Many2one('contract.modality', string="Modality")
    contract_type = fields.Selection(
        selection=[('supplying_and_maintenance', 'Supplying & Maintenance'),
                   ('maintenance', 'Maintenance'),
                   ('supplying', 'Supplying'),
                   ('3rd_party', '3rd Party'),
                   ('demo', 'Demo'),
                   ('n.a', 'N.A'),
                   ('other', 'Other'),
                   ('installation_only', 'Installation Only')],
        string="Contract Type" ,store=True)
    starting_date = fields.Date(string="Starting Date")
    pac_date = fields.Date(string="PAC Date")
    eoc_date = fields.Date(string="EOC Date")
    contract_id = fields.Many2one('contract.contract', string="Contract")
    province = fields.Many2one('contract.province', string="Province")
    price = fields.Float(string='Price')
    active_device = fields.Integer(string="Active Device")
    active_warranty =fields.Integer(string="Active Warranty")
    active_maintenance = fields.Integer(string="Active Maintenance")
    active_contract = fields.Integer(string="Active Contract")
    expired_contract = fields.Integer(string="Expired Contract")

    def init(self):
        tools.drop_view_if_exists(self.env.cr, "contract_report")
        self.env.cr.execute("""CREATE or REPLACE VIEW contract_report as (
                    SELECT
                        min(r.id) as id,
                        r.site as site,
                        r.supplier as partner_id,
                        r.modality as modality,
                        r.contract_type as contract_type,
                        r.starting_date as starting_date,
                        r.pac_date as pac_date,
                        r.eoc_date as eoc_date,
                        r.contract_id as contract_id,
                        r.x_studio_province as province,
                        r.price as price,
                        sum(CASE WHEN r.eoc_date >= CURRENT_DATE THEN 1 ELSE 0 END) as active_device,
                        sum(CASE WHEN r.is_contract_in_warranty = True THEN 1 ELSE 0 END) as active_warranty,
                        sum(CASE WHEN r.is_active_maintenance = True THEN 1 ELSE 0 END) as active_maintenance,
                        (select count(id) from contract_contract where contract_contract.is_eoc = true and contract_contract.active = true) as active_contract,
                        (select count(id) from contract_contract where contract_contract.is_eoc = false and contract_contract.active = true) as expired_contract
                    FROM
                        contract_product r 
                    GROUP BY
                        r.site,
                        r.supplier,
                        r.modality,
                        r.contract_type,
                        r.starting_date,
                        r.pac_date,
                        r.eoc_date,
                        r.contract_id,
                        r.x_studio_province,
                        r.price
                    )""")
