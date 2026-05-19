import base64
import io
import logging

import xlsxwriter
import json
from odoo.tools import json_default

from odoo import models, fields, _, api
from odoo.exceptions import UserError
from ast import literal_eval

_logger = logging.getLogger(__name__)


class SaleOrderInherit(models.Model):
    _inherit = 'sale.order'

    is_to_print_subunit_pricing = fields.Boolean(
        string="Is to print sub units pricing", default=False)
    total_of_exchange_products = fields.Monetary(string="Exchange Value",
                                                 readonly=True, default=0,
                                                 copy=False,
                                                 compute='compute_total_of_exchange_products',
                                                 search='_exchange_value_search')
    select_all_lines = fields.Boolean(
        string="Select All Items As Exchange Items", default=False, copy=False)
    is_cancel_btn_visible = fields.Boolean(
        compute='compute_is_cancel_btn_visible')
    iq = fields.Char(string="IQ Number")
    # signed_by = fields.Many2one('res.partner', 'Signed By',
    #                             help='Name of the person that signed the SO.',
    #                             copy=False)
    contract_id = fields.Many2one('contract.contract', string="Contract",
                                  copy=False)
    # setting Zahraa Raad Salman as default user
    user = fields.Many2one('res.users', string="User",
                           default=lambda self: self.env.ref('__export__.res_users_624_fa634c88'))
    has_exchange_product = fields.Boolean(string="Has exchange product",
                                          compute='compute_has_exchange_product')
    invoice_payment_state = fields.Selection(selection=[
        ('due_payment', 'Due Payment'),
        ('partially_paid', 'Partial Paid'),
        ('fully_paid', 'Fully Paid')],
        string='Payment Status', compute='compute_invoice_payment_state',
        store=True)
    site_id = fields.Many2one('contract.site', string="Site", compute="compute_site_and_province")
    province = fields.Many2one("contract.province", string="Province", compute="compute_site_and_province")
    sn_number = fields.Char(string="SN number", compute="compute_site_and_province")
    is_purchase_order_created = fields.Boolean(copy=False)
    analytic_account_id = fields.Many2one(
        'account.analytic.account',
        string='Analytic Account',
        help="The analytic account related to the sale order"
    )

    @api.depends('team_id')
    def _compute_warehouse_id(self):
        self.warehouse_id = self.team_id.default_warehouse_id

    @api.onchange('related_offering_record')
    def onchange_related_offering_record(self):
        for rec in self:
            rec.related_offering_record.related_sale_order = self._origin.id

    def compute_site_and_province(self):
        for rec in self:
            task = self.env['project.task'].search([("sale_order_id", '=', rec.id)],limit=1)
            rec.site_id = task.site_id
            rec.province = task.province
            rec.sn_number = task.sn

    @api.model
    def action_send_invoice_overdue_mails(self):
        invoice_direct = self.env['account.move'].search([
            ('ref', 'ilike', 'direct sale'),
            ('move_type', '=', 'out_invoice')
        ])
        invoice_direct.is_direct_sales = True
        team_ids = self.env['crm.team'].search([])
        overdue_sales_report_id = self.env.ref(
            'custom_sales.action_report_pdf_overdue_sales')

        for team in team_ids:
            # Normal Invoices
            invoice_ids = self.env['account.move'].search([
                ('move_type', '=', 'out_invoice'),
                ('state', 'not in', ['draft', 'cancel']),
                ('team_id', '=', team.id),
                ('is_direct_sales', '=', False)
            ], order='invoice_user_id ASC,invoice_date ASC')

            # Direct Sale Invoices
            direct_sale_invoice_ids = self.env['account.move'].search([
                ('move_type', '=', 'out_invoice'),
                ('state', 'not in', ['draft', 'cancel']),
                ('team_id', '=', team.id),
                ('is_direct_sales', '=', True)
            ], order='invoice_user_id ASC,invoice_date ASC')

            currencies = invoice_ids.mapped(
                'currency_id') + direct_sale_invoice_ids.mapped('currency_id')

            # Process Invoice Records
            references = list(set(invoice_ids.mapped('ref')))
            invoice_records = []

            for ref in references:
                invoices = invoice_ids.filtered(lambda inv: inv.ref == ref)
                invoices_due = invoices.filtered(lambda
                                                     inv: inv.invoice_date_due <= fields.Date.today() and inv.status_in_payment != 'paid')
                invoices_remaining = invoices.filtered(lambda
                                                           inv: inv.invoice_date_due > fields.Date.today() and inv.status_in_payment != 'paid')

                if invoices_due:
                    record = {
                        'source_document': invoices_due[0].invoice_origin,
                        'reference': ref,
                        'customer': invoices_due[
                            0].invoice_partner_display_name,
                        'sales_person': invoices_due[0].invoice_user_id.name,
                        'total': sum(invoices.mapped('amount_total')),
                        'amount_due': sum(
                            invoices_due.mapped('amount_residual')),
                        'currency': invoices_due[0].currency_id,
                        'remaining': sum(
                            invoices_remaining.mapped('amount_residual')),
                        'due_date': invoices_due[-1].invoice_date_due,
                        'is_fi': invoices_due[0].is_financial_instrument
                    }
                    invoice_records.append(record)

            # Direct Sale Invoices
            for rec in direct_sale_invoice_ids:
                if rec.invoice_date_due <= fields.Date.today():
                    record = {
                        'source_document': rec.invoice_origin,
                        'reference': rec.ref,
                        'customer': rec.invoice_partner_display_name,
                        'sales_person': rec.invoice_user_id.name,
                        'total': rec.amount_total,
                        'amount_due': rec.amount_residual,
                        'currency': rec.currency_id,
                        'remaining': 0,
                        'due_date': rec.invoice_date_due,
                        'is_fi': rec.is_financial_instrument
                    }
                    if record['amount_due']:
                        invoice_records.append(record)

            if invoice_records:
                # Calculate totals by currency
                total = {}
                for currency in currencies:
                    matching_items = sum(
                        [item['amount_due'] for item in invoice_records if
                         item.get('currency') == currency])
                    if matching_items:
                        total[currency] = matching_items

                ## ===================== PDF REPORT ============================
                report_service = self.env['ir.actions.report']
                pdf_content, report_format = report_service._render_qweb_pdf(
                    overdue_sales_report_id.report_name,
                    None,
                    data={'data': invoice_records, 'total': total}
                )
                pdf_attachment = self.env['ir.attachment'].create({
                    'name': 'Overdue Sales Report - %s.pdf' % team.name,
                    'type': 'binary',
                    'datas': base64.b64encode(pdf_content),
                    'res_model': 'account.move',
                    'res_id': self.id,
                    'mimetype': 'application/pdf',
                })

                ## ===================== XLSX REPORT ============================
                xlsx_output = io.BytesIO()
                workbook = xlsxwriter.Workbook(xlsx_output, {'in_memory': True})
                self.generate_xlsx_report(workbook, {'data': invoice_records,
                                                     'total': total}, self)
                workbook.close()
                xlsx_output.seek(0)
                xlsx_content = xlsx_output.read()

                xlsx_attachment = self.env['ir.attachment'].create({
                    'name': 'Overdue Sales Report - %s.xlsx' % team.name,
                    'type': 'binary',
                    'datas': base64.b64encode(xlsx_content),
                    'res_model': 'account.move',
                    'res_id': self.id,
                    'mimetype': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                })

                ## ===================== SEND EMAIL ============================
                email_template = self.env.ref(
                    'custom_sales.mail_template_overdue_sales')

                email_to = []

                if team.user_ids:
                    email_to = team.user_ids.employee_id.mapped('work_email')

                if team.user_id and team.user_id.employee_id.work_email:
                    email_to.append(team.user_id.employee_id.work_email)

                ctx = {
                    'email_to': ",".join(email_to),
                    'email_cc': 'fadi.sabah@alitkan.com,abdullah.kasim@alitkan.com,sinan.nahab@alitkan.com,aaisha.jamal@alitkan.com',
                    'team': team.name,
                }

                # Attach both PDF and XLSX
                email_template.attachment_ids = [(4, pdf_attachment.id),
                                                 (4, xlsx_attachment.id)]
                email_template.with_context(ctx).send_mail(False,
                                                           force_send=True)

                # Clean up
                email_template.attachment_ids = [(5, 0, 0)]
                pdf_attachment.unlink()
                xlsx_attachment.unlink()

    @api.model
    def set_invoice_payment_state(self):
        sale_order_ids = self.env['sale.order'].search([])
        for order in sale_order_ids:
            order.compute_invoice_payment_state()

    @api.depends('invoice_ids.status_in_payment')
    def compute_invoice_payment_state(self):
        for order in self:
            if len(order.invoice_ids.ids) == 0:
                order.invoice_payment_state = False
            else:
                invoice_ids = self.env['account.move'].search(
                    [('state', '!=', 'cancel'),
                     ('id', 'in', order.invoice_ids.ids)])
                if not invoice_ids:
                    order.invoice_payment_state = False
                else:
                    payment_status = invoice_ids.mapped(
                        'status_in_payment')
                    result = True
                    states = ''
                    for state in payment_status:
                        if state != 'paid':
                            result = False
                            if state == 'in_payment':
                                states = 'partially_paid'
                                break
                            break
                        else:
                            result = True
                    if result:
                        order.invoice_payment_state = 'fully_paid'
                    elif not result and states == 'partially_paid':
                        order.invoice_payment_state = 'partially_paid'
                    else:
                        order.invoice_payment_state = 'due_payment'

    def compute_has_exchange_product(self):
        for rec in self:
            if rec.order_line:
                for line in rec.order_line:
                    if line.is_exchange:
                        rec.has_exchange_product = True
                        break
                    else:
                        rec.has_exchange_product = False
            else:
                rec.has_exchange_product = False

    def view_related_contracts(self):
        """Open the related contract in form view."""
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Contract',
            'res_model': 'contract.contract',
            'view_mode': 'form',
            'views': [(False, 'form')],
            'res_id': self.contract_id.id,
            'target': 'current',
        }

    def action_create_contract(self):
        if self.contract_id:
            raise UserError(
                _("Already exist a contract for this sale order"))
        else:
            product_lines = []
            for line in self.order_line:
                product_lines.append((0, 0, {
                    'product_id': line.product_id.id,
                    "product_char": line.product_id.name,
                    "price": line.price_subtotal,
                    "qty": line.product_uom_qty,
                    'config': line.config.id if line.config else False,
                }))
            vals = {'iq': self.iq,
                    'partner_id': self.partner_id.id,
                    'contract_signed_by': self.signed_by,
                    'signed_date': self.signed_on,
                    'number': self.project_num,
                    'product_lines': product_lines}

            contract_id = self.env['contract.contract'].create(vals)
            self.contract_id = contract_id.id

    def compute_is_cancel_btn_visible(self):
        if self.env.user.has_group(
                'sales_team.group_sale_manager') and self.state not in [
            'cancel', 'done']:
            self.is_cancel_btn_visible = True
        else:
            self.is_cancel_btn_visible = False

    @api.onchange('select_all_lines')
    def enable_all_is_exchange(self):
        if self.select_all_lines:
            for rec in self.order_line:
                rec.is_exchange = True
        else:
            for rec in self.order_line:
                rec.is_exchange = False

    @api.depends('state', 'order_line.is_exchange')
    def compute_total_of_exchange_products(self):
        for rec in self:
            if rec.state == 'sale' or rec.state == 'done':
                tot = sum(rec.order_line.filtered(
                    lambda line: line.is_exchange).mapped('price_subtotal'))
                rec.total_of_exchange_products = tot
            else:
                rec.total_of_exchange_products = 0.0

    def _exchange_value_search(self, operator, value):
        if operator == '>':
            res = self.env['sale.order'].search([])
            res = res.filtered(
                lambda rec: value > rec.total_of_exchange_products)
            return [('id', 'in', res.ids)]

        elif operator == '<':
            res = self.env['sale.order'].search([])
            res = res.filtered(
                lambda rec: value < rec.total_of_exchange_products)
            return [('id', 'in', res.ids)]
        elif operator == '>=':
            res = self.env['sale.order'].search([])
            res = res.filtered(
                lambda rec: value >= rec.total_of_exchange_products)
            return [('id', 'in', res.ids)]
        elif operator == '<=':
            res = self.env['sale.order'].search([])
            res = res.filtered(
                lambda rec: value <= rec.total_of_exchange_products)
            return [('id', 'in', res.ids)]

        elif operator == '=':
            res = self.env['sale.order'].search([])
            res = res.filtered(
                lambda rec: value == rec.total_of_exchange_products)
            return [('id', 'in', res.ids)]
        elif operator == '!=':
            res = self.env['sale.order'].search([])
            res = res.filtered(
                lambda rec: value != rec.total_of_exchange_products)
            return [('id', 'in', res.ids)]

    def action_confirm(self):
        """ Confirm the given quotation(s) and set their confirmation date.

        If the corresponding setting is enabled, also locks the Sale Order.

        :return: True
        :rtype: bool
        :raise: UserError if trying to confirm cancelled SO's
        """
        fsm_id = self.env.context.get('fsm_task_id')
        fsm_new_stage = self.env.context.get('new_stage')
        if fsm_id:
            if fsm_new_stage == 'Offer approved':
                return False
        for order in self:
            error_msg = order._confirmation_error_message()
            if error_msg:
                raise UserError(error_msg)

        self.order_line._validate_analytic_distribution()

        for order in self.filtered(
                lambda order: order.partner_id not in order.message_partner_ids):
            order.message_subscribe([order.partner_id.id])

        self.write(self._prepare_confirmation_values())
        users = self.env['ir.config_parameter'].sudo().get_param(
            'sale.confirm_activity_user_ids')
        activity = self.env['mail.activity.type'].search([]).filtered(
            lambda m: m.name == "To Do"
        )
        for so in self:
            so_activity_ids = []
            for user_id in literal_eval(users):
                mail_activity = self.env['mail.activity'].create({
                    'res_id': so.id,
                    'res_model_id': self.env['ir.model'].sudo()._get('sale.order').id,
                    'activity_type_id': activity.id,
                    'summary': 'Invoice Creation Required',
                    'user_id': user_id,
                })
                so_activity_ids.append(mail_activity.id)
            so.write({'confirm_activity_ids': ([(6, 0, so_activity_ids)])})

        # Context key 'default_name' is sometimes propagated up to here.
        # We don't need it and it creates issues in the creation of linked records.
        context = self._context.copy()
        context.pop('default_name', None)
        self.with_context(context)._action_confirm()
        user = self[:1].create_uid
        if user and user.sudo().has_group('sale.group_auto_done_setting'):
            # Public user can confirm SO, so we check the group on any record creator.
            self.action_lock()

        if self.env.context.get('send_email'):
            self._send_order_confirmation_mail()
        return True

    def action_cancel(self):
        active_invoices = self.invoice_ids.filtered(
            lambda x: x.state != 'cancel')
        active_pickings = self.picking_ids.filtered(
            lambda x: x.state not in ['cancel', 'draft'])
        if active_invoices:
            raise UserError(
                _("You can't cancel a sale order having active invoices."))
        if active_pickings:
            raise UserError(
                _("You can't cancel a sale order having delivery slip not in "
                  "draft or canceled."))
        else:
            self.total_of_exchange_products = 0
            return self.write({'state': 'cancel'})

    def action_create_purchase_order(self):
        if not self.order_line:
            raise UserError(_("Order lines are empty"))
        for vendor in self.order_line.mapped('vendor_id'):
            if vendor:
                order_line = self.order_line.search([('vendor_id', '=', vendor.id), ('order_id', '=', self.id)])
                purchase_order_vals = {
                    "partner_id": vendor.id,
                    "origin": self.name,
                    "date_planned": fields.Datetime.now()
                }
                po_order_lines = []
                for so_order_line in order_line:
                    po_order_lines.append((0, 0, {
                        "product_id": so_order_line.product_id.id,
                        "price_unit": so_order_line.vendor_price,
                        "product_qty": so_order_line.product_uom_qty,
                        "name": so_order_line.product_id.name,
                        "product_uom": so_order_line.product_uom.id}))
                purchase_order_vals["order_line"] = po_order_lines
                purchase_order_id = self.env["purchase.order"].create(
                    purchase_order_vals)
                self.is_purchase_order_created = True

    def view_related_purchase(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Purchase Orders',
            'res_model': 'purchase.order',
            'views': [(False, 'list'),
                      ((False, 'form'))],
            'domain': [('origin', '=', self.name)],
        }

    def action_overdue_sales_report_excel(self):
        data = {'record_id': self.id}
        return {
            'type': 'ir.actions.report',
            'data': {'model': 'sale.order', 'options': json.dumps(data, default=json_default),
                     'output_format': 'xlsx', 'report_name': 'Overdue Sales Report'},
            'report_type': 'xlsx'}

    def generate_xlsx_report(self, workbook, data, objs):
        sheet = workbook.add_worksheet('Report')
        head_format = workbook.add_format({
            'align': 'center',
            'bold': True,
            'font_size': '10px',
        })
        data_format = workbook.add_format({
            'font_size': '10px',
        })
        sheet.write(0, 0, '#', head_format)
        sheet.write(0, 1, 'Sale Order', head_format)
        sheet.write(0, 2, 'Reference', head_format)
        sheet.write(0, 3, 'Customer', head_format)
        sheet.write(0, 4, 'Due Date', head_format)
        sheet.write(0, 5, 'Sales Person', head_format)
        sheet.write(0, 6, 'Total', head_format)
        sheet.write(0, 7, 'Amount Due', head_format)
        sheet.write(0, 8, 'Amount Remaining', head_format)

        date_style = workbook.add_format(
            {'text_wrap': True, 'num_format': 'dd/mm/yyyy',
             'font_size': '10px', })

        j = 1
        i = 1
        for invoice in data['data']:
            sheet.write(j, 0, i, data_format)
            i = i + 1
            sheet.write(j, 1, invoice['source_document'], data_format)
            sheet.write(j, 2, invoice['reference'], data_format)
            sheet.write(j, 3, invoice['customer'], data_format)
            sheet.set_column(j, 4, None, date_style)
            sheet.write(j, 4, str(invoice['due_date']), data_format)
            sheet.write(j, 5, invoice['sales_person'], data_format)

            amount_total = invoice['total']
            amount_residual = invoice['amount_due']
            amount_remaining = invoice['remaining']
            currency = invoice['currency']

            # Use string formatting to add commas and currency symbol
            amount_total_with_currency = "{:,.2f} {}".format(amount_total,
                                                             currency.symbol)
            amount_residual_with_currency = "{:,.2f} {}".format(
                amount_residual, currency.symbol)
            amount_remaining_with_currency = "{:,.2f} {}".format(
                amount_remaining, currency.symbol)
            if invoice['is_fi']:
                sheet.write(j, 6, "F.I" + amount_total_with_currency, data_format)
            else:
                sheet.write(j, 6, amount_total_with_currency, data_format)
            sheet.write(j, 7, amount_residual_with_currency, data_format)
            sheet.write(j, 8, amount_remaining_with_currency, data_format)
            j = j + 1

        for total in data['total']:
            j = j + 2
            sheet.write(j, 3, 'Due total in ' + total.name + '(' + total.symbol + '):', head_format)
            total_due = "{:,.2f} {}".format(
                data['total'][total], total.symbol)
            sheet.write(j, 4, total_due, data_format)
