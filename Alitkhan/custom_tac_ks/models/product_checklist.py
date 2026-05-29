from odoo import fields, models, api, _


class ProductChecklist(models.Model):
    _name = "product.checklist"
    _description = "Product Checklist"
    _rec_name = 'product_id'

    product_id = fields.Many2one('product.product',string="Product")
    checklist_item_ids = fields.One2many('checklist.item', 'product_check_list_id', string='Checklist')


class ChecklistItems(models.Model):
    _name = 'checklist.item'
    _description = 'Checklist Item'

    product_check_list_id = fields.Many2one('product.checklist', string="Product Checklist")
    checklist_item = fields.Char(string='Checklist')


class ChecklistLines(models.Model):
    _name = "checklist.line"
    _description = "Checklist Line"

    component_id = fields.Many2one('component.product')
    checklist_line_ids = fields.One2many("checklist.item.line", "checklist_line_id", string="Checklist")

class ChecklistItemLines(models.Model):
    _name = "checklist.item.line"
    _description = "Checklist Item Line"

    checklist_line_id= fields.Many2one("checklist.line")
    checklist_item = fields.Char(string='Checklist')
    is_checked = fields.Boolean(string='Checked')
    remark = fields.Text(string="Note")


class ComponentProducts(models.Model):
    _name = 'component.product'
    _description = "Component Product"

    ticket_id = fields.Many2one('tac.ks.ticket', string="Ticket")
    product_ids = fields.Many2many('product.product', string='Products',
                                   compute="_compute_product", store=True)
    product_id = fields.Many2one('product.product', string="Product", domain="[('id','in', product_ids)]")
    progress = fields.Integer("Progress", compute="compute_progress")
    serial_number_id = fields.Many2one('serial.number', string='Serial Number')
    images = fields.Many2many("ir.attachment",string="Image")

    @api.model
    def create(self, vals):
        res = super(ComponentProducts, self).create(vals)
        images = res.mapped('images')
        images.write({
            'res_id': res.id,
        })
        return res

    def compute_progress(self):
        for rec in self:
            checklist = self.env['checklist.line'].search([('component_id', '=', rec.id)])
            total_checklist = len(checklist.checklist_line_ids)
            true_checklist = len(checklist.checklist_line_ids.search([('is_checked', '=', True), ('checklist_line_id', '=', checklist.id)]))
            if total_checklist:
                rec.progress = (true_checklist/total_checklist)*100
            else:
                rec.progress = 0

    @api.depends('ticket_id')
    def _compute_product(self):
        for rec in self:
            rec.product_ids = self.env['product.checklist'].search([]).product_id

    def action_show_checklist(self):
        checklist = self.env['product.checklist'].search(
            [('product_id', '=', self.product_id.id)])
        checklist_items = checklist.checklist_item_ids.mapped('checklist_item')
        wizard = self.env['checklist.line'].search(
            [('component_id', '=', self.id)])
        if not wizard:
            wizard = self.env['checklist.line'].create(
            {   'component_id': self.id,
                'checklist_line_ids' : [(0,0,{"checklist_item": item}) for item in checklist_items]})
        return {
            'name': _('Checklist'),
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'checklist.line',
            'target': 'new',
            'res_id': wizard.id
        }
