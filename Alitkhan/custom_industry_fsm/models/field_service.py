from datetime import timedelta

from odoo import models, fields, _, api
from collections import defaultdict
from odoo.tools import float_round
from odoo.exceptions import UserError
from odoo.osv import expression
from odoo.addons.industry_fsm_stock.models.project_task import Task



class CustomProductProductFsm(models.Model):
    _inherit = 'product.product'

    fsm_quantity = fields.Float('Material Quantity', compute="_compute_fsm_quantity", inverse="_inverse_fsm_quantity", search="_search_fsm_quantity")

    def _inverse_fsm_quantity(self):
        task = self._get_contextual_fsm_task()
        if task:
            SaleOrderLine_sudo = self.env['sale.order.line'].sudo()
            sale_lines_read_group = SaleOrderLine_sudo._read_group([
                ('order_id', '=', task.sale_order_id.id),
                ('product_id', 'in', self.ids),
                ('task_id', '=', task.id)],
                ['product_id', 'sequence'],
                ['id:array_agg'])
            sale_lines_per_product = defaultdict(lambda: self.env['sale.order.line'])
            for product, __, ids in sale_lines_read_group:
                sale_lines_per_product[product.id] |= SaleOrderLine_sudo.browse(ids)
            for product in self:
                sale_lines = sale_lines_per_product.get(product.id, self.env['sale.order.line'])
                all_editable_lines = sale_lines.filtered(lambda l: l.qty_delivered == 0 or l.qty_delivered_method == 'manual' or not l.order_id.locked)
                diff_qty = product.fsm_quantity - sum(sale_lines.mapped('product_uom_qty'))
                if all_editable_lines:  # existing line: change ordered qty (and delivered, if delivered method)
                    if diff_qty > 0:
                        vals = {
                            'product_uom_qty': all_editable_lines[0].product_uom_qty + diff_qty,
                        }
                        if task.under_warranty:
                            vals['price_unit'] = 0
                        if product.service_type == 'manual':
                            vals['qty_delivered'] = all_editable_lines[0].product_uom_qty + diff_qty
                        all_editable_lines[0].with_context(fsm_no_message_post=True).write(vals)
                        continue
                    # diff_qty is negative, we remove the quantities from existing editable lines:
                    for line in all_editable_lines:
                        new_line_qty = max(0, line.product_uom_qty + diff_qty)
                        diff_qty += line.product_uom_qty - new_line_qty
                        if product.service_type == 'manual':
                            line.with_context(fsm_no_message_post=True).qty_delivered = new_line_qty
                        line.with_context(fsm_no_message_post=True).product_uom_qty = new_line_qty
                        if task.under_warranty:
                            line.price_unit = 0
                        if diff_qty == 0:
                            break
                elif diff_qty > 0:  # create new SOL
                    vals = {
                        'order_id': task.sale_order_id.id,
                        'product_id': product.id,
                        'product_uom_qty': diff_qty,
                        'product_uom': product.uom_id.id,
                        'task_id': task.id
                    }
                    if task.under_warranty:
                        vals['price_unit'] = 0
                    if product.service_type == 'manual':
                        vals['qty_delivered'] = diff_qty
                    if task.sale_order_id.order_line:
                        vals['sequence'] = max(task.sale_order_id.order_line.mapped('sequence')) + 1
                    sol_sudo = SaleOrderLine_sudo.create(vals)
            # if not sum(task.sale_order_id.order_line.mapped('product_uom_qty')):
            #     task.sudo().sale_order_id.sudo().unlink()

    # def _compute_fsm_quantity(self):
    #     task_id = self.env.context.get('fsm_task_id')
    #     if task_id:
    #         task = self.env['project.task'].browse(task_id)
    #         product_map = {sol.product_id.id: sol.product_uom_qty for sol in
    #                        task.sale_order_id.order_line}
    #         for product in self:
    #             product.fsm_quantity = product_map.get(product.id, 0)
    #     else:
    #         self.fsm_quantity = False

    # def search_fsm_quantity(self, operator, value):
    #     if operator == '>':
    #         res = self.env['product.product'].search([])
    #         res = res.filtered(lambda rec: value > rec.fsm_quantity)
    #         return [('id', 'in', res.ids)]
    #
    #     elif operator == '<':
    #         res = self.env['product.product'].search([])
    #         res = res.filtered(lambda rec: value < rec.fsm_quantity)
    #         return [('id', 'in', res.ids)]
    #     elif operator == '>=':
    #         res = self.env['product.product'].search([])
    #         res = res.filtered(lambda rec: value >= rec.fsm_quantity)
    #         return [('id', 'in', res.ids)]
    #     elif operator == '<=':
    #         res = self.env['product.product'].search([])
    #         res = res.filtered(lambda rec: value <= rec.fsm_quantity)
    #         return [('id', 'in', res.ids)]
    #     elif operator == '=':
    #         res = self.env['product.product'].search([])
    #         res = res.filtered(lambda rec: value == rec.fsm_quantity)
    #         return [('id', 'in', res.ids)]
    #     elif operator == '!=':
    #         res = self.env['product.product'].search([])
    #         res = res.filtered(lambda rec: value != rec.fsm_quantity)
    #         return [('id', 'in', res.ids)]

#---------------------------------------------------------------------------------------

    # def fsm_add_quantity(self):
    #     task_id = self.env.context.get('fsm_task_id')
    #     if task_id:
    #         task = self.env['project.task'].browse(task_id)
    #         if not task.sale_order_id:
    #         if not task.sale_order_id:
    #             task._fsm_ensure_sale_order()
    #             # don't add material on confirmed SO to avoid inconsistence with the stock picking
    #         if task.fsm_done:
    #             return False
    #
    #         # project user with no sale rights should be able to add materials
    #         SaleOrderLine = self.env['sale.order.line']
    #         if self.env.user.has_group('project.group_project_user'):
    #             task = task.sudo()
    #             SaleOrderLine = SaleOrderLine.sudo()
    #
    #         sale_line = SaleOrderLine.search(
    #             [('order_id', '=', task.sale_order_id.id),
    #              ('product_id', '=', self.id)],
    #             limit=1)
    #
    #         if sale_line:  # existing line: increment ordered qty (and delivered, if delivered method)
    #             vals = {
    #                 'product_uom_qty': sale_line.product_uom_qty + 1
    #             }
    #             if sale_line.qty_delivered_method == 'manual':
    #                 vals['qty_delivered'] = sale_line.qty_delivered + 1
    #             sale_line.with_context(fsm_no_message_post=True).write(vals)
    #         else:  # create new SOL
    #             vals = {
    #                 'order_id': task.sale_order_id.id,
    #                 'product_id': self.id,
    #                 'product_uom_qty': 1,
    #                 'product_uom': self.uom_id.id,
    #                 'price_unit': 0.0,
    #             }
    #             if self.service_type == 'manual':
    #                 vals['qty_delivered'] = 1
    #
    #             # Note: force to False to avoid changing planned hours when modifying product_uom_qty on SOL
    #             # for materials. Set the current task for service to avoid re-creating a task on SO cnofirmation.
    #             if self.type == 'service':
    #                 vals['task_id'] = task_id
    #             else:
    #                 vals['task_id'] = False
    #             if task.sale_order_id.pricelist_id.discount_policy == 'without_discount':
    #                 sol = SaleOrderLine.new(vals)
    #                 sol._onchange_discount()
    #                 vals.update({'discount': sol.discount or 0.0})
    #             sale_line = SaleOrderLine.create(vals)
    #
    #     return True

    #------------------------------------------------------------------------

    # def fsm_remove_quantity(self):
    #     task_id = self.env.context.get('fsm_task_id')
    #     if task_id:
    #         task = self.env['project.task'].browse(task_id)
    #
    #         # don't remove material on confirmed SO to avoid inconsistence with the stock picking
    #         if task.fsm_done:
    #             return False
    #
    #         # project user with no sale rights should be able to remove materials
    #         SaleOrderLine = self.env['sale.order.line']
    #         if self.env.user.has_group('project.group_project_user'):
    #             task = task.sudo()
    #             SaleOrderLine = SaleOrderLine.sudo()
    #
    #         sale_line = SaleOrderLine.search(
    #             [('order_id', '=', task.sale_order_id.id),
    #              ('product_id', '=', self.id)],
    #             limit=1)
    #         if sale_line:
    #             vals = {
    #                 'product_uom_qty': sale_line.product_uom_qty - 1
    #             }
    #             if sale_line.qty_delivered_method == 'manual':
    #                 vals['qty_delivered'] = sale_line.qty_delivered - 1
    #
    #             if vals[
    #                 'product_uom_qty'] <= 0 and task.sale_order_id.state != 'sale':
    #                 sale_line.unlink()
    #             else:
    #                 sale_line.with_context(fsm_no_message_post=True).write(vals)
    #         sale_line_ids_count = SaleOrderLine.search_count(
    #             [('order_id', '=', task.sale_order_id.id)])
    #         if sale_line_ids_count == 1:
    #             task.sudo().sale_order_id.sudo().unlink()
    #     return True
    #-----------------------------------------------------------------------------------


class CustomTask(models.Model):
    _inherit = "project.task"

    maintenance_iq = fields.Char(string="Maintenance Iq")
    is_maintenance_iq_readonly = fields.Boolean(
        string="Is maintenance iq visible",
        compute='compute_is_maintenance_iq_readonly')
    total_working_days = fields.Integer(string="Total Working Days",
                                        compute='compute_total_working_days')
    total_working_fridays = fields.Integer(string="Total working fridays",
                                           compute='compute_total_working_fridays')
    service_type = fields.Selection(selection=[('backup', 'Backup'),('re-export', 'Re-export'),
                                              ('backup&re-export', 'Backup & Re-export')])
    color = fields.Integer('Color Index')
    product_reservation_count = fields.Integer(compute="compute_reservation_count")


    def compute_reservation_count(self):
        for rec in self:
            rec.product_reservation_count = self.env['product.reservation'].search_count([('serial_number', '=', self.sn)])

    def write(self, vals):
        if vals.get('service_type'):
            data = {
                'backup': 3,
                're-export': 10,
                'backup&re-export': 4
            }
            vals['color'] = data[vals.get('service_type')]
        elif vals.get('color', None):
            if self.service_type:
                vals.pop('color')

        res = super().write(vals)

        # Second: Field Service access unit logic
        if 'sale_order_id' in vals and vals['sale_order_id']:
            field_service_access_unit = self.env['access.units'].sudo().search([
                ('name', '=ilike', 'Field Service')
            ], limit=1)
            if field_service_access_unit:
                self.sale_order_id.write({
                    'access_unit_ids': [(4, field_service_access_unit.id)]
                })

        return res

    def action_view_product_reservation(self):
        domain = [('serial_number', '=', self.sn)]
        return{
            'type': 'ir.actions.act_window',
            'name': 'Product Reservations',
            'res_model': 'product.reservation',
            'view_mode': 'list,form',
            'domain': domain,
            'context': {
                'default_serial_number': self.sn,
            },
        }

    @api.depends('planned_date_begin', 'date_deadline')
    def compute_total_working_days(self):
        for rec in self:
            if rec.date_deadline and rec.planned_date_begin:
                if rec.date_deadline == rec.planned_date_begin:
                    rec.total_working_days = 1
                else:
                    total_days = rec.date_deadline - rec.planned_date_begin
                    rec.total_working_days = total_days.days + 1
            else:
                # Set to 0 if dates are not properly set
                rec.total_working_days = 0

    @api.depends('planned_date_begin', 'date_deadline')
    def compute_total_working_fridays(self):
        for rec in self:
            for record in self:
                if record.planned_date_begin and record.date_deadline:
                    current_date = record.planned_date_begin
                    total_fridays = 0
                    while current_date <= record.date_deadline:
                        if current_date.weekday() == 4:  # Friday has the weekday value of 4
                            total_fridays += 1
                        current_date += timedelta(days=1)
                    record.total_working_fridays = total_fridays
                else:
                    record.total_working_fridays = 0

    def compute_is_maintenance_iq_readonly(self):
        for rec in self:
            if self.env.user.has_group('logistics.logistics_user'):
                rec.is_maintenance_iq_readonly = True
            else:
                rec.is_maintenance_iq_readonly = False

    @api.constrains('planned_date_begin', 'date_end')
    def _set_calander_event(self):
        if self.planned_date_begin and self.date_end:
            self.event_ids.unlink()
            users = [user for user in self.co_user_ids]

            if self.user_id:
                users.append(self.user_id)

            for user_id in users:
                event = self.env['calendar.event'].create({
                    'name': self.name,
                    'send_email_to_attendees': False,
                    'start': self.planned_date_begin,
                    'stop': self.date_end,
                    'partner_id': user_id.partner_id.id,
                    'user_id': user_id.id,
                    'partner_ids': [user_id.partner_id.id],
                    'privacy': 'confidential',
                })
                self.event_ids += event

    @api.constrains('parent_id', 'child_ids')
    def _check_subtask_level(self):
        for task in self:
            if task.parent_id and task.child_ids:
                pass

    def set_fsm_quantity(self, quantity):
        task = self._get_contextual_fsm_task()
        # project user with no sale rights should be able to change material quantities
        if not task or quantity and quantity < 0 or not self.env.user.has_group('project.group_project_user'):
            return
        self = self.sudo()

        # don't add material on locked SO
        if task.sale_order_id.sudo().locked:
            return False
        # ensure that the task is linked to a sale order
        task._fsm_ensure_sale_order()
        wizard_product_lot = self.action_assign_serial(from_onchange=True)
        if wizard_product_lot:
            return wizard_product_lot
        self.fsm_quantity = float_round(quantity or 0, precision_rounding=self.uom_id.rounding)
        return True

    def _fsm_create_sale_order(self):
        """ Create the SO from the task, with the 'service product' sales line and link all timesheet to that line it """
        self.ensure_one()
        if not self.partner_id:
            raise UserError(_('A customer should be set on the task to generate a worksheet.'))

        SaleOrder = self.env['sale.order']
        if self.env.user.has_group('project.group_project_user'):
            SaleOrder = SaleOrder.sudo()

        domain = ['|', ('company_id', '=', False),
                  ('company_id', '=', self.company_id.id)]
        team = self.env['crm.team'].sudo()._get_default_team_id(domain=domain)
        access_unit = self.env['access.units'].sudo().search(
            [('name', '=ilike', 'Field Service')])
        vals = {
            'partner_id': self.partner_id.id,
            'company_id': self.company_id.id,
            'analytic_account_id': self.project_id.account_id.id,
            'team_id': team.id if team else False,
            'access_unit_ids': access_unit.ids,
            'client_order_ref': self.maintenance_iq,
        }

        sale_order = SaleOrder.create(vals)
        # update after creation since onchange_partner_id sets the current user
        sale_order.write({'user_id': False})

        self.sale_order_id = sale_order

    def action_fsm_view_material(self):
        """Action to view the product catalogue"""
        domain = [('sale_ok', '=', True), '|',
                  ('company_id', '=', self.company_id.id),
                  ('company_id', '=', False)]
        if self.project_id and self.project_id.timesheet_product_id:
            domain = expression.AND([domain, [
                ('id', '!=', self.project_id.timesheet_product_id.id)]])
        deposit_product = self.env['ir.config_parameter'].sudo().get_param(
            'sale.default_deposit_product_id')
        if deposit_product:
            domain = expression.AND([domain, [('id', '!=', deposit_product)]])

        modality_approval_stage = self.env['project.task.type'].search(
            [('modality_stage', '=', True),
             ('name', 'ilike', 'Modality Approval')])
        search_view = self.env.ref('industry_fsm_sale.industry_fsm_sale_product_catalog_inherit_search_view')
        if self.stage_id.sequence > modality_approval_stage.sequence and self.material_line_product_count > 0:
            if self.env.user.has_groups('helpdesk.group_helpdesk_manager'):
                kanban_view = self.env.ref('industry_fsm_sale.industry_fsm_sale_product_catalog_kanban_view')
                return {
                    'type': 'ir.actions.act_window',
                    'name': _('Add Products'),
                    'res_model': 'product.product',
                    'views': [(kanban_view.id, 'kanban'), (False, 'form')],
                    'search_view_id': [search_view.id, 'search'],
                    'domain': domain,
                    'context': {
                        'fsm_mode': True,
                        'create': self.env['product.template'].has_access('create'),
                        'fsm_task_id': self.id,  # avoid 'default_' context key as we are going to create SOL with this context
                        'pricelist': self.partner_id.property_product_pricelist.id,
                        'order_id': self.sale_order_id.id,
                        **self.sale_order_id.sudo()._get_action_add_from_catalog_extra_context(),
                        'hide_qty_buttons': self.sale_order_id.sudo().locked,
                        'default_invoice_policy': 'delivery',
                        'product_catalog_currency_id': self.currency_id.id,
                        'search_default_fsm_quantity': self.state == '1_done',
                    },
                    'help': _("""<p class="o_view_nocontent_smiling_face">
                                    No products found. Let's create one!
                                </p><p>
                                    Keep track of the products you are using to complete your tasks, and invoice your customers for the goods.
                                    Tip: using kits, you can add multiple products at once.
                                </p><p>
                                    When your task is marked as done, your stock will be updated automatically. Simply choose a warehouse
                                    in your profile from where to draw stock.
                                </p>""")
                }
            else:
                kanban_view = self.env.ref(
                    'custom_industry_fsm.view_product_product_kanban_material_for_helpdesk_support_center')

                return {
                    'type': 'ir.actions.act_window',
                    'name': _('Choose Products'),
                    'res_model': 'product.product',
                    'views': [(kanban_view.id, 'kanban'), (False, 'form')],
                    'search_view_id': [search_view.id, 'search'],
                    'domain': domain,
                    'context': {
                        'fsm_mode': True,
                        'create': self.env[
                            'product.template'].has_access('create'),
                        'fsm_task_id': self.id,
                        # avoid 'default_' context key as we are going to create SOL with this context
                        'pricelist': self.partner_id.property_product_pricelist.id if self.partner_id else False,
                        'partner': self.partner_id.id if self.partner_id else False,
                        'search_default_goods': 1,
                        'search_default_fsm_quantity': 1,
                        'hide_qty_buttons': self.fsm_done
                    },
                    'help': _("""<p class="o_view_nocontent_smiling_face">
                                    Create a new product
                                </p><p>
                                    You must define a product for everything you sell or purchase,
                                    whether it's a storable product, a consumable or a service.
                                </p>""")
                }
        else:
            kanban_view = self.env.ref('industry_fsm_sale.industry_fsm_sale_product_catalog_kanban_view')
            obj = {
                'type': 'ir.actions.act_window',
                'name': _('Add Products'),
                'res_model': 'product.product',
                'views': [(kanban_view.id, 'kanban'), (False, 'form')],
                'search_view_id': [search_view.id, 'search'],
                'domain': domain,
                'context': {
                    'fsm_mode': True,
                    'create': self.env['product.template'].has_access('create'),
                    'fsm_task_id': self.id,
                    # avoid 'default_' context key as we are going to create SOL with this context
                    'pricelist': self.sudo().partner_id.property_product_pricelist.id,
                    'order_id': self.sudo().sale_order_id.id,
                    **self.sudo().sale_order_id._get_action_add_from_catalog_extra_context(),
                    'hide_qty_buttons': self.sudo().sale_order_id.locked,
                    'default_invoice_policy': 'delivery',
                    'product_catalog_currency_id': self.currency_id.id,
                    'search_default_fsm_quantity': 1,
                },
                'help': _("""<p class="o_view_nocontent_smiling_face">
                                                No products found. Let's create one!
                                            </p><p>
                                                Keep track of the products you are using to complete your tasks, and invoice your customers for the goods.
                                                Tip: using kits, you can add multiple products at once.
                                            </p><p>
                                                When your task is marked as done, your stock will be updated automatically. Simply choose a warehouse
                                                in your profile from where to draw stock.
                                            </p>""")
            }
            return obj

    #++++++++++++++++++++++++++++++++++++++++++++++

    def change_access_unit_of_sale_order(self):
        field_service = self.env['project.task'].search([('sale_order_id','!=', False)])
        spare_access_unit = self.env['access.units'].sudo().search(
            [('name', '=ilike', 'Spare Parts')])
        service_access_unit = self.env['access.units'].sudo().search(
            [('name', '=ilike', 'Field Service')])
        for service in field_service:
            if service.sale_order_id.access_unit_ids:
                service.sale_order_id.write({
                    'access_unit_ids': [(3,spare_access_unit.id)]})
                service.sale_order_id.write({
                    'access_unit_ids': [(4,service_access_unit.id)]})


def _fsm_create_sale_order(self):
    """ Create the SO from the task, with the 'service product' sales line and link all timesheet to that line it """
    self.ensure_one()
    if not self.partner_id:
        raise UserError(_('A customer should be set on the task to generate a worksheet.'))

    SaleOrder = self.env['sale.order']
    if self.env.user.has_group('project.group_project_user'):
        SaleOrder = SaleOrder.sudo()

    domain = ['|', ('company_id', '=', False),
              ('company_id', '=', self.company_id.id)]
    team = self.env['crm.team'].sudo()._get_default_team_id(domain=domain)
    access_unit = self.env['access.units'].sudo().search(
        [('name', '=ilike', 'Field Service')])
    vals = {
        'partner_id': self.partner_id.id,
        'company_id': self.company_id.id,
        'analytic_account_id': self.project_id.account_id.id,
        'team_id': team.id if team else False,
        'access_unit_ids': access_unit.ids,
        'client_order_ref': self.maintenance_iq,
    }

    sale_order = SaleOrder.create(vals)
    # update after creation since onchange_partner_id sets the current user
    sale_order.write({'user_id': False})

    self.sale_order_id = sale_order


def _fsm_ensure_sale_order(self):
    """ this function monkey patches the method
        in industry_fsm_stock/models/project_task.py > _fsm_ensure_sale_order
        to stop auto confirm """
    self.ensure_one()
    if not self.sale_order_id:
        self._fsm_create_sale_order()
    sale_order = self.sale_order_id
    if self.env.user.has_group('project.group_project_user'):
        sale_order = self.sale_order_id.sudo()
    if not sale_order.project_id:
        sale_order.project_id = self.project_id
    return self.sale_order_id

Task._fsm_create_sale_order = _fsm_create_sale_order

Task._fsm_ensure_sale_order = _fsm_ensure_sale_order