# -*- coding: utf-8 -*-
from markupsafe import Markup

from odoo import models, fields, api, _
from odoo.exceptions import UserError
import datetime
import json



class LogisticsShipment(models.Model):
    _name = 'logistics.shipment'
    _description = 'Shipment'
    _inherit = ['mail.thread']
    _rec_name = "name_seq"

    _status = [('draft', 'Draft'), ('active', 'Active'), ('done', 'Done')]

    status = fields.Selection(_status, default='draft')
    name_seq = fields.Char(string="id", required=True, copy=False, readonly=True, index=True, default="New")
    contract_ids = fields.Many2many('contract.contract',relation="shipment_contracts",column1="col1",column2="col2",string='Contract')
    origin_ids = fields.Many2many('purchase.order', string="Origin",relation="shipment_purchase",column1="col1",column2="col2")
    origin_is_selected = fields.Boolean(default=False)
    customer = fields.Many2one('res.partner',string='Partner')
    vendor = fields.Many2one("res.partner",string="Vendor")
    multi_vendor = fields.Boolean(string="Multi-Vendor")
    tags_ids = fields.Many2many('logistics.shipment.tags',string="Tags")
    shipment_total = fields.Float(compute="_compute_shipment_total",string='Shipment Total')
    shipment_lines = fields.One2many('logistics.shipment.line', 'shipment_id', string='Shipment Products')
    # purchase_orders = fields.One2many('logistics.shipment.pos', 'shipment_id', string="Purchase Orders") # Deprecated - By Ahmed Naseem
    total_po = fields.Float(string="Total",compute="get_total_po")
    ratio = fields.Float(string="Items Price to Shipment Cost Ratio",compute="calculate_ratio")
    current_location = fields.Many2one("res.country.state",string="Current Location",compute="compute_current_location")
    routes_count = fields.Integer(compute="compute_routes_count")
    color = fields.Integer('Color Index', compute="change_colore_on_kanban")
    stage_id = fields.Many2one('shipment.stage', string='Stage', ondelete='restrict', tracking=True, index=True, copy=False,group_expand='_read_group_stage_ids')
    document_count = fields.Integer(compute="compute_documents_count")

    
    @api.constrains("stage_id")
    def notify_callback(self):
        for rcd in self:
            if rcd.stage_id.is_notification_stage:
                if rcd.stage_id.notify_by == "channel":
                    rcd.notify_channel(channel_name=rcd.stage_id.channel_name,object=rcd)
                else:
                    rcd.notify_user(object=rcd,user_ids=rcd.stage_id.notified_ids)
            else:
                pass
        


    def notify_channel(self,channel_name,object):
        channel_id = self.env['discuss.channel'].search([('name', '=', channel_name)])
        if not channel_id:
            channel_id = self.env['discuss.channel'].create({
                'name': channel_name,
            })
        notification = Markup(
            '<div class="logistics.shipment">'
            '<a href="#" class="o_redirect" data-oe-model = "logistics.shipment" data-oe-id="%i">%s</a><'
            '/div>') % (object.id, object.name_seq)
        channel_id.message_post(
            body='Automated Message :Shipment'+ ' ' + notification + ' has been moved to ' + object.stage_id.name + ' Stage.',
            message_type='comment',
            subtype_xmlid=self.env.ref('mail.mt_comment').id,
            partner_ids=[partner_id.id for partner_id in channel_id.channel_partner_ids])


    def notify_user(self,object,user_ids):
        partners=[user.partner_id.id for user in user_ids]
        notification = Markup(
        '<div class="logistics.shipment"><a href="#" class="o_redirect" data-oe-model = "logistics.shipment" data-oe-id="%i">%s</a></div>') % (object.id, object.name_seq)
        self.message_post(
            body= 'Automated Message :Shipment'+ ' ' + notification + ' has been moved to ' + object.stage_id.name + ' Stage.',
            message_type='notification',
            subtype_xmlid='mail.mt_comment',
            partner_ids= partners)

    def compute_documents_count(self):
        for rcd in self:
            documents = self.env["shipment.document"].search([("shipment_id","=",rcd.id)])
            if documents:
                rcd.document_count = len(documents)
            else:
                rcd.document_count = False

    def compute_routes_count(self):
        for rcd in self:
            routes = self.env["shipment.route"].search([("shipment_id","=",rcd.id)],order="date")
            if routes:
                rcd.routes_count = len(routes)
            else:
                rcd.routes_count = False

    def compute_current_location(self):
        for rcd in self:
            routes = self.env["shipment.route"].search([("shipment_id","=",rcd.id)],order="date")
            if routes:
                rcd.current_location = routes[-1].location_id.id
            else:
                rcd.current_location = False

    def change_colore_on_kanban(self):
        for record in self:
            color = 0
            if record.status == 'draft':
                color = 3
            elif record.status == 'active':
                color = 4
            elif record.status == 'done':
                color = 10
            else:
                color = 5
            record.color = color

    @api.model
    def _read_group_stage_ids(self,stages="",domain="",order=""):
        stage_ids = self.env['shipment.stage'].search([])
        return stage_ids


    def action_confirm(self):
        self.status = "active"

    def action_done(self):
        self.status = "done"

    def action_reset(self):
        self.status = "draft"
    
    def calculate_ratio(self):
        for rcd in self:
            if rcd.total_po > 0 and rcd.shipment_total > 0:
                rcd.ratio = rcd.total_po / rcd.shipment_total
            else:
                rcd.ratio = 0

    def get_total_po(self):
        for rcd in self:
            total = 0
            pos = self.env["purchase.order"].search([("related_shipment_id","=",rcd.id)])
            for item in pos:
                total += item.amount_total
            rcd.total_po = total


    def _compute_shipment_total(self):
        shipment_total=0
        for line in self.shipment_lines:
            shipment_total+=line.amount_total
        self.shipment_total=shipment_total


    @api.onchange('origin_ids')
    def show_get_pos_button(self):
        if(self.origin_ids):
            self.origin_is_selected=True
        else:
            self.origin_is_selected=False

    def get_from_pos(self):
        self.write({"shipment_lines":[(5)]})
        contracts=[]
        for po in self.origin_ids:
            for line in po.order_line:
                self.shipment_lines.create({"shipment_id":self.id,'product_id':line.product_id.id,'qty':line.product_qty, "unit_price":line.price_unit,"amount_total":line.price_unit*line.product_qty})
            if po.contract_id:
                contracts.append(po.contract_id.id)
        self.contract_ids = contracts
    

    def redirect_to_pos(self,context={}):
        form_view_id = self.env.ref("purchase.purchase_order_form").id
        tree_view_id = self.env.ref("purchase.purchase_order_tree").id
        context.update({"default_related_shipment_id":self.id})
                
        return {
            'type': 'ir.actions.act_window',
            'name': 'Purchase Orders',
            'view_type': 'form',
            'view_mode': 'list',
            'res_model': 'purchase.order',
            'views': [(tree_view_id,'list'),(form_view_id, 'form')],
            'domain': [('related_shipment_id', '=', self.id)],
            'target': 'current',
            'context':context,            
        }

    def redirect_to_routes(self,context={}):
        form_view_id = self.env.ref("logistics.shipment_routes_form").id
        tree_view_id = self.env.ref("logistics.shipment_route_tree").id
        context.update({"default_shipment_id":self.id})
        return {
            'type': 'ir.actions.act_window',
            'name': 'Routes',
            'view_type': 'form',
            'view_mode': 'list',
            'res_model': 'shipment.route',
            'views': [(tree_view_id,'list'),(form_view_id, 'form')],
            'domain': [('shipment_id', '=', self.id)],
            'target': 'current',
            'context':context,            
        }

    def redirect_to_documents(self,context={}):
        form_view_id = self.env.ref("logistics.shipment_document_form").id
        tree_view_id = self.env.ref("logistics.shipment_document_tree").id
        context.update({"default_shipment_id":self.id})
        return {
            'type': 'ir.actions.act_window',
            'name': 'Documents',
            'view_type': 'form',
            'view_mode': 'list',
            'res_model': 'shipment.document',
            'views': [(tree_view_id,'list'),(form_view_id, 'form')],
            'domain': [('shipment_id', '=', self.id)],
            'target': 'current',
            'context':context,            
        }

class ShipmentStage(models.Model):
    _name="shipment.stage"

    name = fields.Char('Stage Name', required=True, translate=True)
    sequence = fields.Integer('Sequence', default=1, help="Used to order stages. Lower is better.")
    is_notification_stage = fields.Boolean(string="Notify users at this stage?") #Used to unhide notified users field
    notify_by = fields.Selection([("channel","Channel"),("direct","Directly to user")],string="Notify By",default="direct") 
    channel_name = fields.Char(string="Channel Name")
    notified_ids = fields.Many2many(comodel_name="res.users",relation="stage_user_rel",column1="stage_col",column2="user_col",string="Users to notfiy") #This field will holds user ids of the users to notify when a shipment reaches this stage

class LogisticsShipmentLine(models.Model):
    _name = 'logistics.shipment.line'
    _description = 'logistics.shipment.line'

    shipment_id = fields.Many2one('logistics.shipment',string='Shipment ID')
    product_id = fields.Many2one('product.product', string="Product")
    vendors = fields.Char()
    qty = fields.Integer()
    unit_price = fields.Float()
    amount_total = fields.Float()


class LogisticsShipmentTags(models.Model):

    _name = 'logistics.shipment.tags'
    _description = 'logistics.shipment.tags'
    _rec_name="name"

    name = fields.Char(string='Tag')
    color = fields.Integer()


class LogisticsShipmentTransTypes(models.Model):
    _name = 'logistics.shipment.transtypes'
    _description = 'logistics.shipment.transtypes'
    _rec_name = "name"

    name = fields.Char(string="Name")    
    is_transport = fields.Boolean(string="Transportation Expense",help="Is this a transportation expense?")



class PurchaseOrderExpense(models.Model):
    _inherit="purchase.order"
    
    related_shipment_id = fields.Many2one("logistics.shipment",string="Related Shipment", readonly=True)
    type_id = fields.Many2one("logistics.shipment.transtypes",string="Shipment Expense Type")
    location_id = fields.Many2one("res.country.state",string="From",groups="logistics.logistics_manager")
    location_dest_id = fields.Many2one("res.country.state",string="To",groups="logistics.logistics_manager")



class ShipmentRoute(models.Model):
    _name="shipment.route"

    shipment_id = fields.Many2one("logistics.shipment")
    location_id = fields.Many2one("res.country.state",string="Current Location")
    date = fields.Date(string="Arrival Date")
    notes = fields.Char(string="Notes")


class ShipmentDocument(models.Model):
    _name="shipment.document"
    _inherit = ['mail.thread']

    shipment_id = fields.Many2one("logistics.shipment")
    name = fields.Char(string="Document Name",required=True)
    file_name = fields.Char() #download name
    file = fields.Binary(string="Document Upload",required=True)
    requires_action = fields.Boolean(string="Does this document require action from other users?")
    comments = fields.Text(string="Comments")
    notified_ids = fields.Many2many(comodel_name="res.users",relation="document_user_rel",column1="document_col",column2="user_col_l",string="Users to notfiy") 

    def send_notifications(self):
        partners=[user.partner_id.id for user in self.notified_ids]
        notification = Markup(
        '<div class="shipment.document"><a href="#" class="o_redirect" data-oe-model = "shipment.document" data-oe-id="%i">%s</a></div>') % (self.id, self.name)
        self.message_post(
            body= 'Automated Message :Document'+ ' ' + notification + ' Needs your action ',
            message_type='notification',
            subtype_xmlid='mail.mt_comment',
            partner_ids= partners)