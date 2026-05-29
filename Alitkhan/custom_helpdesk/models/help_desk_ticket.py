import datetime
import re
from dateutil.relativedelta import relativedelta
from odoo import api, fields, models, _
from odoo.exceptions import UserError
from odoo.models import NewId
from markupsafe import Markup
from odoo.addons.itkan_helpdesk.models.project_task import ProjectTaskExt
from odoo.addons.itkan_helpdesk.models.helpdesk_ticket import HelpDeskTicket
# from custom_addons_1.itkan_helpdesk.models.helpdesk_ticket import HelpDeskTicket


# class HelpDeskTicketMpatch(HelpDeskTicket):

def write(self, values):
    if values.get('stage_id'):
        new_stage_id = self.env['helpdesk.stage'].browse([values['stage_id']])
        if new_stage_id.cancel_activities:
            self.activity_ids.unlink()
            if self.field_service_id:
                self.field_service_id.activity_ids.unlink()
        # this section is to allow moving tickets forward only
        if self.stage_id.sequence > new_stage_id.sequence:
            raise UserError(_("You can only move tickets forward"))
        elif new_stage_id.is_restrict_ticket_move:
            if self.field_service_id:
                fs_stage = self.env['project.task.type'].search([
                    ('project_ids', '=',
                     self.field_service_id.project_id.id),
                    ('helpdesk_stage_id', '=', new_stage_id.id)])
                if self.field_service_id.stage_id.sequence < fs_stage.sequence:
                    raise UserError(_("You can't directly move to this stage."))
            else:
                raise UserError(_("You can't directly move to this stage."))


        # this section is to check whether the user have the premission of
        # moving from the selected ticket

        if (self.stage_id.limited_users and
                not self.stage_id.only_notification and
                self.env.user.id not in self.stage_id.limited_users.ids and
                not self.env.context.get('active_fs_ticket')):
            raise UserError(
                _("You don't have permission to move the ticket to this stage"))

        # this section is to check whether the new stage must be within
        # contract
        if self.ticket_type_id.name != 'Note':
            if new_stage_id.must_be_within_contract and self.stage_id.is_first and not self.exception_id:
                if not (self.unit_id and self.contract_is_valid):
                    raise UserError(_(
                        f"You cannot move this ticket directly to the {new_stage_id.name} stage "
                        f"because it is not within contract"
                    ))

            ticket_stage_with_must_be_out_of_contract = self.env[
                'helpdesk.stage'].search(
                [('must_be_out_of_contract', '=', True)])
            if self.stage_id.is_first:
                if new_stage_id.name != 'Cancelled':
                    if self.exception_id:
                        if self.contract_is_valid and new_stage_id.must_be_out_of_contract:
                            if not self.exception_id.limit_helpdesk_approval:
                                raise UserError(_(f"You can't move to"
                                                  f" {new_stage_id.name} "
                                                  f"stage because contract "
                                                  f"is valid for the ticket"
                                                  f"."))
                        elif self.contract_is_valid and not new_stage_id.must_be_out_of_contract:
                            if self.exception_id.limit_helpdesk_approval:
                                raise UserError(
                                    _("You can't bypass Approval stage "
                                      "because an exception is applied "
                                      "on the ticket."))
                        else:
                            if not self.contract_is_valid:
                                if self.exception_id.bypass_helpdesk_approval:
                                    if new_stage_id.must_be_out_of_contract:
                                        raise UserError(
                                            _("You can't move to this stage"
                                              " because an exception is "
                                              "applied on the ticket."))
                                elif self.exception_id.limit_helpdesk_approval and not new_stage_id.must_be_out_of_contract:
                                    raise UserError(
                                        _("You can't bypass Approval stage "
                                          "because an exception is applied "
                                          "on the ticket."))
                                else:
                                    for stage in ticket_stage_with_must_be_out_of_contract:
                                        if new_stage_id.sequence > stage.sequence:
                                            raise UserError(
                                                _("You can't bypass "
                                                  "Approval stage."))

                    else:
                        if self.contract_is_valid and new_stage_id.must_be_out_of_contract:
                            raise UserError(
                                _(f"You can't move to {new_stage_id.name}"
                                  f" stage because contract is valid for "
                                  f"the ticket."))
                        elif not self.contract_is_valid:
                            for stage in ticket_stage_with_must_be_out_of_contract:
                                if new_stage_id.sequence > stage.sequence:
                                    raise UserError(
                                        _("You can't bypass Approval stage."))

        # this section is to check whether the new stage require full
        # resources
        if new_stage_id.require_full_resource and not self.resources_are_full:
            raise UserError(
                _(f"This ticket can not be moved to {new_stage_id.name} "
                  f"stage because some resources are missing"))
        if self.stage_id.name in ['In Progress', 'Pending Approval', 'Pending Order', 'Field Service Done',
                                  'Offer Approved', 'قيد التنفيذ']:
            if (new_stage_id.name in ['Pending Approval', 'Pending Order', 'Field Service Done', 'Done',
                                      'Offer Approved'] and
                    self.field_service_id.stage_id.name != 'Done' and self.field_service_id.stage_id.helpdesk_stage_id != new_stage_id):
                raise UserError(
                    _(f"This ticket can not be moved to '{new_stage_id.name}' "
                      f"stage because the field service ticket is in '{self.field_service_id.stage_id.name}' stage."))
        if new_stage_id.is_field_service_ticket_exist:
            if not self.field_service_id:
                raise UserError(
                    _(f"This ticket can not be moved to '{new_stage_id.name}' "
                      f"stage because there is no field service ticket."))

    return super(HelpDeskTicket, self).write(values)
HelpDeskTicket.write = write

@api.model_create_multi
def create(self, values):
    record = super(HelpDeskTicket, self).create(values)
    service_report_attachments = record.mapped('service_report_attachments')
    service_report_attachments.write({
        'res_id': record.id,
    })

    if not record.job_number:
        job_number = self.env['ir.sequence'].next_by_code(
            'helpdesk.ticket') or 'New'
        if job_number:
            record.job_number = job_number


    else:
        parent_ticket = record.parent_ticket
        parent_ticket.child_ticket = record.id
        if parent_ticket.field_service_id:
            project_task = parent_ticket.field_service_id
            task_done_stage = self.env['project.task.type'].search(
                [('project_ids', '=', project_task.project_id.id),
                 ('state', '=', 'done')])
            if len(task_done_stage) < 1:
                raise UserError(
                    "Could not find a project stage that matches the "
                    "requirements. Please contact your support")
            if len(task_done_stage) == 1:
                project_task.stage_id = task_done_stage.id
            if len(task_done_stage) > 1:
                raise UserError(
                    f"Multiple done stages detected. "
                    f"Please contact your support"
                    f":\n{', '.join(task_done_stage.mapped('name'))}")

        ticket_done_stage = self.env['helpdesk.stage'].search(
            [('fold', '=', True), ('cancelled_stage', '=', False),
             ('team_ids', 'in', parent_ticket.team_id.id)])
        if parent_ticket:
            if len(ticket_done_stage) < 1:
                raise UserError(
                    "Could not find a project stage that matches the "
                    "requirements. Please contact your support")
            if len(ticket_done_stage) == 1:
                parent_ticket.with_context(
                    active_fs_ticket=True).stage_id = ticket_done_stage.id
            if len(ticket_done_stage) > 1:
                raise UserError(
                    f"Multiple done stages detected."
                    f" please contact your support"
                    f":\n{', '.join(ticket_done_stage.mapped('name'))}")
    return record
HelpDeskTicket.create = create



# class ProjectTaskMpatch(models.Model):
#     _inherit = 'project.task'
#

def write(self, values):
    if 'planned_date_begin' in values.keys() or 'planned_date_end' in values.keys():
        if self.planned_date_begin or self.planned_date_end:
            activity_id = self.env['mail.activity'].search(
                [('res_id', '=', self.id),
                 ('activity_type_id', '=', self.env.ref(
                     'custom_helpdesk.mail_activity_task_range_update').id)])
            activity_id.action_feedback(feedback="")
            users = self.co_user_ids.ids
            users.extend(self.user_ids.ids)
            note = _("The Task range for the ticket is updated.")
            if not self.stage_id.is_not_send_notification:
                for user in users:
                    self.activity_schedule(
                        'custom_helpdesk.mail_activity_task_range_update',
                        note=note,
                        user_id=user)

    # checking if user has access
    # doing from here instead of from the record rule model because I had
    # several issues
    field_service_manager_group = self.env.ref(
        'industry_fsm.group_fsm_manager')
    for rec in self:
        if rec.is_fsm and not (
                values.get('related_helpdesk_ticket') or values.get(
            'event_ids')) and rec.env.user.id not in rec.user_ids.ids and rec.env.user.id not in field_service_manager_group.users.ids and rec.env.user.id not in rec.co_user_ids.ids:
            raise UserError(
                "You don't have permission to make changes to this task")
    if values.get(
            "stage_id") and self.related_helpdesk_ticket and not self.related_helpdesk_ticket.child_ticket \
            and self.related_helpdesk_ticket.ticket_type_id.require_service_report:
        # checking if service report is required & uploaded
        new_stage = self.env['project.task.type'].browse(
            [values['stage_id']])
        if new_stage.require_service_report and not self.service_report_docs:
            raise UserError(
                _("You need to upload a service report document before "
                  "moving the task to this stage"))

    if values.get("stage_id") and not values.get("date_last_stage_update"):

        new_stage_id = self.env['project.task.type'].browse(
            values['stage_id'])

        if self.related_helpdesk_ticket.ticket_type_id.name == 'Defect':
            project_ids = self.env['project.project'].search(
                [('name', '=ilike', 'Field Service')]).ids
            modality_stages = self.env['project.task.type'].search(
                [('modality_stage', '=', True),
                 ('project_ids', 'in', project_ids)], limit=1)
            ticket_stage_with_must_be_out_of_contract = self.env[
                'project.task.type'].search(
                [('ticket_must_be_invalid', '=', True),
                 ('project_ids', 'in',
                  self.env['project.project'].search(
                      [('name', 'ilike', 'Field Service')]).ids)])
            if self.stage_id.name == 'New':
                if new_stage_id.state != 'cancelled':
                    if self.material_line_product_count > 0:

                        for modality_stage in modality_stages:
                            if new_stage_id.sequence > modality_stage.sequence:
                                if not self.related_helpdesk_ticket.exception_id:
                                    if self.material_line_product_count > 0:
                                        raise UserError(
                                            _("You can't bypass Modality"
                                              " Approval."))

                                else:
                                    if self.material_line_product_count > 0:
                                        raise UserError(
                                            _("You can't bypass Modality"
                                              " Approval."))

                        if self.stage_id.name == 'Modality Approval' and self.stage_id.modality_stage:
                            if new_stage_id.ticket_must_be_invalid and self.is_contract_valid:
                                if self.related_helpdesk_ticket.exception_id.limit_field_service_approval and new_stage_id.ticket_must_be_invalid:
                                    pass
                                elif self.is_contract_valid and not self.is_contract_in_warranty and \
                                        new_stage_id.ticket_must_be_invalid and not \
                                        self.related_helpdesk_ticket.exception_id.bypass_field_service_approval:
                                    pass
                                else:
                                    raise UserError(
                                        _(f"This ticket can not be moved to"
                                          f" {new_stage_id.name} stage"
                                          f" because the contract is valid "
                                          f"for the ticket"))
                            else:
                                if not self.is_contract_valid:
                                    for stage in ticket_stage_with_must_be_out_of_contract:
                                        if new_stage_id.sequence <= stage.sequence:
                                            pass
                                        elif self.related_helpdesk_ticket.exception_id:

                                            if self.related_helpdesk_ticket.exception_id.bypass_field_service_approval:
                                                if new_stage_id.ticket_must_be_invalid:
                                                    raise UserError(
                                                        _("You can't move "
                                                          "to this stage "
                                                          "because an "
                                                          "exception reason"
                                                          " is applied on "
                                                          "the ticket."))
                                            elif self.related_helpdesk_ticket.exception_id.limit_fiield_service_approval and new_stage_id.sequence > stage.sequence:
                                                raise UserError(
                                                    _(f"This ticket can not"
                                                      f" be moved to "
                                                      f"{new_stage_id.name}"
                                                      f" stage because it's"
                                                      f" already out of "
                                                      f"contract"))
                                            else:
                                                raise UserError(
                                                    _(f"This ticket can not be moved to {new_stage_id.name} "
                                                      f"stage because it's already out of contract"))
                                        else:
                                            raise UserError(
                                                _(f"This ticket can not be moved to {new_stage_id.name} "
                                                  f"stage because it's already out of contract"))
                                else:
                                    if not self.is_contract_in_warranty:
                                        if self.related_helpdesk_ticket.exception_id.bypass_field_service_approval:
                                            if new_stage_id.ticket_must_be_invalid:
                                                raise UserError(
                                                    _("You can't move to this stage because an exception reason is "
                                                      "applied on the ticket"))
                                        else:
                                            raise UserError(
                                                _("You can't bypass approval stage. Because the contract is"
                                                  "in out of warranty."))
                                    elif self.related_helpdesk_ticket.exception_id.limit_field_service_approval and new_stage_id.id not in ticket_stage_with_must_be_out_of_contract.ids:
                                        raise UserError(
                                            _("You can't bypass Approval stage because an exception reason"
                                              " is applied on the ticket."))
                    else:
                        stage_ids = self.env['project.task.type'].search(
                            [('name', '=ilike', 'Repairing')])
                        for stage in stage_ids:
                            if new_stage_id.sequence < stage.sequence:
                                raise UserError(
                                    _("You don't need to move to this stage, because no spare parts "
                                      "chosen."))

            elif self.stage_id.name == 'Modality Approval' and self.stage_id.modality_stage:
                if self.is_contract_valid:
                    if self.related_helpdesk_ticket.exception_id:
                        if self.related_helpdesk_ticket.exception_id.limit_field_service_approval:
                            if not new_stage_id.ticket_must_be_invalid:
                                raise UserError(
                                    _("You can't bypass Approval stage because an exception reason"
                                      " is applied on the ticket."))
                        elif not self.is_contract_in_warranty:
                            if self.related_helpdesk_ticket.exception_id.bypass_field_service_approval:
                                if new_stage_id.ticket_must_be_invalid:
                                    raise UserError(
                                        _("You can't move to this stage because an exception reason is applied on"
                                          " the ticket."))

                            else:
                                if not new_stage_id.ticket_must_be_invalid:

                                    raise UserError(
                                        _("You can't bypass approval stage."
                                          " Because the contract is in out "
                                          "of warranty."))
                        else:
                            if new_stage_id.ticket_must_be_invalid:
                                raise UserError(
                                    _("You can't move to this stage because"
                                      " the contract is valid for the"
                                      " ticket."))
                    else:
                        if not self.is_contract_in_warranty:
                            if not new_stage_id.ticket_must_be_invalid:
                                raise UserError(
                                    _("You can't bypass approval stage "
                                      "because the contract is in out"
                                      " of warranty."))
                        else:
                            if new_stage_id.ticket_must_be_invalid:
                                raise UserError(
                                    _("You can't move to this stage because"
                                      " the contract is valid for "
                                      "the ticket."))
                            else:
                                # sale_id = self.env['sale.order'].browse(
                                #     self.sudo().sale_order_id.id)
                                # sale_id.sudo().action_confirm()
                                if self.sudo().sale_order_id.state in {'draft', 'sent'}:
                                    self.sudo().sale_order_id.action_confirm()
                else:
                    for stage in ticket_stage_with_must_be_out_of_contract:
                        if new_stage_id.sequence < stage.sequence:
                            pass
                        elif self.related_helpdesk_ticket.exception_id:
                            if self.related_helpdesk_ticket.exception_id.bypass_field_service_approval:
                                if new_stage_id.ticket_must_be_invalid:
                                    raise UserError(
                                        _("You can't move to this stage "
                                          "because an exception reason is "
                                          "applied on the ticket."))
                            elif self.related_helpdesk_ticket.exception_id.limit_field_service_approval and new_stage_id.sequence > stage.sequence:
                                raise UserError(
                                    _(f"This ticket can not be moved to {new_stage_id.name} "
                                      f"stage because it's already out of contract"))
                            else:
                                if not new_stage_id.ticket_must_be_invalid:
                                    raise UserError(
                                        _(f"This ticket can not be moved to {new_stage_id.name} "
                                          f"stage because it's already out of contract"))
                        else:
                            if not new_stage_id.ticket_must_be_invalid:
                                raise UserError(
                                    _(f"This ticket can not be moved to {new_stage_id.name} "
                                      f"stage because it's already out of contract"))
            elif new_stage_id.name == 'Offer approved':
                # sale_id = self.env['sale.order'].browse(
                #     self.sudo().sale_order_id.id)
                # self.sudo().sale_order_id.sudo().action_confirm()
                self.with_context(fsm_task_id=self.id,new_stage = 'Offer approved').sudo().sale_order_id.sudo().action_confirm()
            elif new_stage_id.name == 'Offer Refused':
                # sale_id = self.env['sale.order'].browse(
                #     self.sudo().sale_order_id.id)
                # sale_id.sudo().action_cancel()
                self.sudo().sale_order_id.sudo().action_cancel()
    res = super(ProjectTaskExt, self).write(values)
    return res
ProjectTaskExt.write = write





class CustomHelpDeskTicket(models.Model):
    _inherit = "helpdesk.ticket"

    def update_filter_action(self):
        filters = self.env['ir.filters'].search([('action_id', 'in', [1191,1310],),('model_id', '=', 'helpdesk.ticket'),('id','not in',[345,374])])
        for rec in filters:
            rec.update({
                'action_id': 1311
            })

    ticket_type_id = fields.Many2one('helpdesk.ticket.type',
                                     string="Ticket Type", required=True)
    call_received_partner_id = fields.Many2one('res.partner',
                                               string="Call Received By",
                                               tracking=True)
    user_id = fields.Many2one('res.users', string='Assigned to', tracking=True,
                              domain=lambda self: ['|', (
                                  'groups_id', 'in', self.env.ref(
                                      'helpdesk.group_helpdesk_user').id), (
                                                       'groups_id', 'in',
                                                       self.env.ref(
                                                           'custom_helpdesk.group_helpdesk_user_no_create').id)])
    contract_id = fields.Many2one("contract.contract", string="Contract",
                                  related="unit_id.contract_id")
    similar_tickets = fields.Char()
    is_resource_set_on_task = fields.Boolean()
    is_resource_set_on_agenda = fields.Boolean()
    field_service_id = fields.Many2one("project.task", string="Field Services",
                                       copy=False)
    exception_id = fields.Many2one("helpdesk.ticket.exception",
                                   string="Exception Reason",
                                   readonly=False)
    exception_id_new = fields.Many2one("helpdesk.ticket.exception",
                                       string="Exception Reason")
    pm_workdone_description = fields.Text()
    is_contract_in_warranty = fields.Boolean(compute='_check_eoc_date')
    call_number = fields.Char("Reported By (Phone Number)",
                              related='partner_id.phone')
    is_view_maintenance_iq = fields.Boolean(
        compute='compute_is_view_maintenance_iq', )
    maintenance_iq = fields.Char(string="Maintenance Iq",
                                 related='field_service_id.maintenance_iq')
    new_maintenance_iq = fields.Char(string="Maintenance Iq",
                                     related='field_service_id.maintenance_iq',
                                     store=True)
    recieve_date = fields.Datetime("Call Received Date", tracking=True,
                                   default=lambda *a: fields.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    date_start = fields.Datetime(string="Starting Date", tracking=True)
    date_end = fields.Datetime(string="Ending Date", tracking=True)
    service_report_attachments = fields.Many2many(comodel_name="ir.attachment",
                                                  relation="attachement_helpdesk_field_service_doc_rel",
                                                  column1="ticket_id",
                                                  column2="attachment_id",
                                                  string="Service report "
                                                         "documents",
                                                  related='field_service_id.service_report_docs'

                                                  )
    resource_lines = fields.One2many("helpdedesk.resource",
                                     "helpdesk_ticket_id", string="Recources",
                                     )
    created_by = fields.Many2one('res.users',
                                 default=lambda self: self.env.user)


    def copy(self, default=None):
        if not self.env.user.has_group(
                'sales_team.group_sale_salesman') and not self.env.user.has_group(
            'account.group_account_invoice'):
            if default is None:
                default = {'sale_order_id': False}
            else:
                default.update({'sale_order_id': False})
        return super(CustomHelpDeskTicket, self).copy(default=default)

    @api.depends('close_hours')
    def _compute_open_hours(self):
        for ticket in self:
            if ticket.create_date:  # fix from https://github.com/odoo/enterprise/commit/928fbd1a16e9837190e9c172fa50828fae2a44f7
                if ticket.close_date:
                    time_difference = ticket.close_date - fields.Datetime.from_string(
                        ticket.create_date)
                else:
                    time_difference = fields.Datetime.now() - fields.Datetime.from_string(
                        ticket.create_date)
                ticket.open_hours = (
                                        time_difference.seconds) / 3600 + time_difference.days * 24
            else:
                ticket.open_hours = 0

    @api.model
    def fields_get(self, allfields=None, attributes=None):
        hide = ['maintenance_iq']
        res = super(CustomHelpDeskTicket, self).fields_get()
        for field in hide:
            res[field]['selectable'] = False
        return res

    @api.onchange('created_by')
    def onchange_created_by(self):
        co_person_job_resource = self.env[
            'helpdedesk.resource.category'].search(
            [('name', '=', 'Co Person Job')], limit=1)
        self.resource_lines = [(5, 0, 0)]
        self.resource_lines = [
            (0, 0, {'categ_id': self.env.ref('itkan_helpdesk.data_enginner').id,
                    'qty': 0}),
            (0, 0,
             {'categ_id': self.env.ref('itkan_helpdesk.data_co_enginner').id,
              'qty': 0}),
            (0, 0,
             {'categ_id': self.env.ref('itkan_helpdesk.data_technicians').id,
              'qty': 0}),
            (0, 0, {'categ_id': self.env.ref('itkan_helpdesk.data_vehicles').id,
                    'qty': 0}),
            (0, 0, {'categ_id': co_person_job_resource.id,
                    'qty': 0}),
        ]

    def assign_maintenance_iq(self):
        helpdesk_ticket = self.env['helpdesk.ticket'].search(
            [('maintenance_iq', '!=', False)])
        for rec in helpdesk_ticket:
            if not rec.new_maintenance_iq:
                rec.new_maintenance_iq = rec.maintenance_iq

    @api.onchange('description')
    def onchange_description(self):
        if self.field_service_id:
            self.field_service_id.description = self.description

    def compute_is_view_maintenance_iq(self):
        for rec in self:
            if self.env.user.has_group('logistics.logistics_user'):
                rec.is_view_maintenance_iq = True
            else:
                rec.is_view_maintenance_iq = False

    @api.onchange('new_maintenance_iq')
    def onchange_new_maintenance_iq(self):
        if self.field_service_id:
            self.field_service_id.maintenance_iq = self.new_maintenance_iq

    def unlink(self):
        """ Method to delete the helpdesk ticket ,its related field service tickets and calendar events created from
        the related field service tickets."""
        if self.field_service_id:
            if self.field_service_id.event_ids:
                for event in self.field_service_id.event_ids:
                    event.sudo().unlink()
            self.field_service_id.unlink()
        return super(CustomHelpDeskTicket, self).unlink()

    @api.onchange('unit_eoc_date')
    def _check_eoc_date(self):
        """ Method to compute whether the contract is valid and contract in warranty or not."""
        for ticket in self:
            if ticket.unit_eoc_date and ticket.unit_eoc_date >= datetime.date.today():
                ticket.contract_is_valid = True
            else:
                ticket.contract_is_valid = False
            starting_date = ticket.unit_id.starting_date
            if starting_date:
                if ticket.unit_id.warranty:
                    warranty_date = starting_date + relativedelta(
                        years=ticket.unit_id.warranty)
                    if warranty_date <= datetime.date.today():
                        ticket.is_contract_in_warranty = False
                    else:
                        ticket.is_contract_in_warranty = True
                else:
                    ticket.is_contract_in_warranty = False
            else:
                ticket.is_contract_in_warranty = False

    @api.onchange('ticket_type_id')
    def onchange_ticket_type(self):
        """ Method to change the exception in the onchange of ticket type."""
        if self.parent_ticket:
            self.exception_id = self.ticket_type_id.subticket_exception_id.id
        else:
            self.exception_id = self.ticket_type_id.exception_id.id

    @api.constrains('ticket_type_id')
    def on_save_ticket_type(self):
        if not self.service_report_id:
            if self.ticket_type_id.require_service_report:
                user_names = self.resource_lines.mapped('user_ids.name')
                co_persons = ', '.join(user_names)
                cars_names = self.resource_lines.mapped('vehicle_ids.name')
                cars_sting = ', '.join(cars_names)
                service_report_id = self.env['service.report'].create({
                    'task_number': '#' + str(self.id),
                    'modality': self.brand_id.id,
                    'province': self.province_id.id,
                    't_type': 'job',
                    'reported_by': self.site_id.site_name,
                    'car': cars_sting,
                    'contract': self.contract_id.id,
                    'site': self.site_id.id,
                    'sn': self.sn,
                    'unit': self.unit_id.product_char if self.unit_id.product_char else self.unit_id.product_id.name,
                    'description': self.description if self.description else '',
                    'resource': co_persons,
                    'engineer': self.user_id[0].partner_id.id if self.user_id else False,
                    'task_id': self.field_service_id.id,
                    'job_number': self.job_number,
                })
                self.service_report_id = service_report_id.id
                self.field_service_id.service_report_id = service_report_id.id

    def _check_resource_overlap(self):
        """ Function to check the resources are overlapped or not."""
        for ticket in self:
            if ticket.date_start and ticket.date_end and (
                    ticket.resource_lines or self.user_id[0]) and type(
                ticket.id) == type(int()):
                # getting all tickets within the same time range
                overlapped_tickets = self.env['helpdesk.ticket'].search([
                    ('stage_id.is_close', '!=', True),
                    ('active', '=', True),
                    ('id', '!=', ticket.id),
                    '|',
                    ('user_id', '!=', False),
                    ('resource_lines', '!=', False),
                    '|',
                    '|',
                    '&',
                    ('date_start', '>=', ticket.date_start),
                    ('date_start', '<=', ticket.date_end),
                    '&',
                    ('date_end', '>=', ticket.date_start),
                    ('date_end', '<=', ticket.date_end),
                    '&',
                    ('date_start', '<=', ticket.date_start),
                    ('date_end', '>=', ticket.date_end),
                ])

                if overlapped_tickets:
                    result = self.env['helpdesk.ticket']
                    for lapped_ticket in overlapped_tickets:
                        # check if the fetched ticket has the same user selected
                        lapped_users = lapped_ticket.resource_lines.mapped(
                            'user_ids.id')
                        if lapped_ticket.user_id:
                            lapped_users.append(lapped_ticket.user_id.id)

                        current_users = ticket.resource_lines.mapped(
                            'user_ids.id')
                        if ticket.user_id:
                            current_users.append(ticket.user_id.id)

                        overlapped_users = any(user for user in lapped_users if
                                               user in current_users)
                        if overlapped_users:
                            result += lapped_ticket

                    return result
                else:
                    return []
            else:
                return []

    def view_overlapped_tickets(self):
        """ Method to return the view of overlapped tickets."""
        lapped_tickets = self._check_resource_overlap()
        if lapped_tickets:

            return {
                'type': 'ir.actions.act_window',
                'name': 'Overlapped Ticket',
                'view_type': 'form',
                'view_mode': 'kanban',
                'res_model': 'helpdesk.ticket',
                'views': [(False, 'kanban'), (False, 'list'), (False, 'form')],
                'domain': [('id', 'in', lapped_tickets.ids),
                           ('stage_id.is_close', '!=', True)],
                'target': 'current'
            }


    @api.onchange("site_id", 'ticket_type_id')
    def _compute_brand(self):
        """ Method to return Modality values based on the site and ticket
        type."""
        res = {}
        brands = []
        rcds = self.env["contract.contract"].search([])
        for item in rcds:
            for product in item.product_lines:
                if product.site.id == self.site_id.id:
                    brands.append(product.modality.id)
        note_ticket_type_id = self.env['helpdesk.ticket.type'].search(
            [('name', '=ilike', 'Note')])
        if self.ticket_type_id.id == note_ticket_type_id.id:
            res['domain'] = {'brand_id': []}
        else:
            res['domain'] = {'brand_id': [("id", "in", brands)]}
        return res

    @api.constrains('user_id')
    def save_assigned_to(self):
        """ Method to create an activity notification for the field service user
         when the user is changed."""
        if self.field_service_id:
            agenda_id = self.env['agenda.agenda'].search(
                [('task_id', '=', self.field_service_id.id)])
            note = _("You have assigned this task")
            if agenda_id:
                self.field_service_id.user_ids = [(6, 0, [self.user_id.id])]
                activity_id = self.env['mail.activity'].search(
                    [('res_id', '=', self.field_service_id.id),
                     ('activity_type_id', '=', self.env.ref(
                         'custom_helpdesk.mail_activity_user_update').id)])
                activity_id.action_feedback(feedback="")
                self.field_service_id.activity_schedule(
                    'custom_helpdesk.mail_activity_user_update',
                    note=note,
                    user_id=self.user_id.id)

    @api.constrains('resource_lines')
    def save_resources(self):
        """ Method to create notification for the agenda users."""
        if self.field_service_id:
            users = self.resource_lines.mapped('user_ids').ids
            vehicles = self.resource_lines.mapped('vehicle_ids').ids
            if len(users) == 0:
                self.field_service_id.co_user_ids = False
            else:
                self.field_service_id.co_user_ids = users
            if len(vehicles) == 0:
                self.field_service_id.vehicle_ids = False
            else:
                self.field_service_id.vehicle_ids = vehicles

            agenda_id = self.env['agenda.agenda'].search(
                [('task_id', '=', self.field_service_id.id)])
            if agenda_id:
                note = _("You have assigned this task")
                activity_id = self.env['mail.activity'].search(
                    [('res_id', '=', self.field_service_id.id),
                     ('activity_type_id', '=', self.env.ref(
                         'custom_helpdesk.mail_activity_resource_update').id)])
                activity_id.action_feedback(feedback="")

                for user in agenda_id.user_ids:
                    self.field_service_id.activity_schedule(
                        'custom_helpdesk.mail_activity_resource_update',
                        note=note,
                        user_id=user.id)

    @api.constrains('stage_id')
    def send_users_notificaiton(self):
        """ Method to send user notification when stage changes. """
        if self.env.user.has_group(
                'helpdesk.group_helpdesk_manager') or self.env.user.has_group(
            'helpdesk.group_helpdesk_user'):
            pass
        elif self.env.user.has_group(
                'custom_helpdesk.group_helpdesk_user_no_create'):
            if self.env.context.get('active_fs_ticket'):
                pass
            else:
                raise UserError(_("You can't directly move to this stage."))

        activity_idd = self.env['mail.activity'].search(
            [('res_id', '=', self.id),
             ('activity_type_id', '=', self.env.ref(
                 'custom_helpdesk.mail_activity_helpdesk_ticket_assigned').id)])
        activity_idd.action_feedback(feedback="")

        # activity_id = self.env['mail.activity'].search(
        #     [('res_id', '=', self.id),
        #      ('activity_type_id', '=', self.env.ref(
        #          'custom_helpdesk.mail_activity_helpdesk_ticket_move').id)])
        activity_id = self.env['mail.activity'].search(
            [('res_id', '=', self.id),
             ('activity_type_id', '=', self.env.ref(
                 'custom_helpdesk.mail_activity_helpdesk_ticket_move_1').id)])

        # activity_id.action_feedback(feedback="")
        activity_id.action_done()

        users = False
        if self.stage_id.modality_stage:
            # modality_id = self.brand_id
            # users = [user.id for user in modality_id.user_ids]
            users = self.brand_id.user_ids.ids

        elif self.stage_id.limited_users and self.stage_id.send_notification and not (
                self.stage_id.only_valid_tickets and not self.contract_is_valid):
            # users = [user.id for user in self.stage_id.limited_users]
            users = self.stage_id.limited_users.ids

        # =============================

        if users:
            note = _("A new ticket has been moved to your stage: %s") % (
                self.display_name)
            for user in users:
                self.activity_schedule(
                    'custom_helpdesk.mail_activity_helpdesk_ticket_move_1',
                    note=note,
                    user_id=user)


    def find_user_list(self):
        """ Method to find all responsible users"""
        user_list = []
        for resource in self.resource_lines:
            for user in resource.user_ids:
                if isinstance(user.id, NewId):
                    user_id = user._origin
                    user_list.append(user_id.id)
                else:
                    user_list.append(user.id)
        user_list.append(self.user_id.id)
        return user_list

    def view_agenda_with_resources(self):
        """ Method to view conflicted agendas"""
        user_list = self.find_user_list()
        tickets = self.env['agenda.agenda'].search(
            [('user_ids', 'in', user_list), '|',
             ('task_id', '!=', self.field_service_id.id),
             ('task_id', '=', False),
             '|',
             '|',
             '&',
             ('date_start', '>=', self.date_start),
             ('date_start', '<=', self.date_end),
             '&',
             ('date_end', '>=', self.date_start),
             ('date_end', '<=', self.date_end),
             '&',
             ('date_start', '<=', self.date_start),
             ('date_end', '>=', self.date_end)])
        if tickets:
            return {
                'type': 'ir.actions.act_window',
                'name': 'FS Tickets',
                'view_type': 'form',
                'view_mode': 'kanban',
                'res_model': 'agenda.agenda',
                'views': [(False, 'list'), (False, 'form')],
                'domain': [('id', 'in', tickets.ids)],
                'target': 'current'
            }

    def view_tickets_with_resources(self):
        """ Method to view conflicted field service tickets."""
        user_list = self.find_user_list()
        tickets = self.env['project.task'].search(
            [('user_id', 'in', user_list), ('is_fsm', '=', True),
             ('id', '!=', self.field_service_id.id),
             ('stage_id.state', '!=', 'done'),
             ('stage_id.state', '!=', 'cancelled'),
             '|',
             '|',
             '&',
             ('planned_date_begin', '>=', self.date_start),
             ('planned_date_begin', '<=', self.date_end),
             '&',
             ('planned_date_end', '>=', self.date_start),
             ('planned_date_end', '<=', self.date_end),
             '&',
             ('planned_date_begin', '<=', self.date_start),
             ('planned_date_end', '>=', self.date_end)])
        if tickets:
            return {
                'type': 'ir.actions.act_window',
                'view_id': self.env.ref(
                    'industry_fsm.project_task_view_kanban_fsm').id,
                'name': 'FS Tickets',
                'view_type': 'kanban',
                'view_mode': 'kanban',
                'res_model': 'project.task',
                'views': [(self.env.ref(
                    'industry_fsm.project_task_view_kanban_fsm').id, 'kanban'),
                          (self.env.ref(
                              'industry_fsm.project_task_view_list_fsm').id,
                           'list'),
                          (self.env.ref(
                              'industry_fsm.project_task_view_form').id,
                           'form')],
                'domain': [('id', 'in', tickets.ids)],
                'target': 'current'
            }

    @api.constrains('user_id', 'date_start', 'date_end', 'resource_lines')
    def onsave_user_id(self):
        """ Method to change users on Agenda and to check is there any
        conflicted agenda's and field service tickets
        within the same task range."""
        user_list = self.find_user_list()
        if self.field_service_id:
            agenda_ids = self.env['agenda.agenda'].search(
                [('task_id', '=', self.field_service_id.id)])
            for agenda_id in agenda_ids:
                if agenda_id:
                    agenda_id.user_ids = [(5, 0, 0)]
                    if len(user_list) == 0:
                        agenda_id.user_ids = False
                    else:
                        agenda_id.user_ids = user_list
        if self.date_start and self.date_end:
            for user in user_list:
                task_ids = self.env['project.task'].search(
                    [('user_ids', 'in', user), ('is_fsm', '=', True),
                     ('id', '!=', self.field_service_id.id),
                     '|',
                     '|',
                     '&',
                     ('planned_date_begin', '>=', self.date_start),
                     ('planned_date_begin', '<=', self.date_end),
                     '&',
                     ('planned_date_end', '>=', self.date_start),
                     ('planned_date_end', '<=', self.date_end),
                     '&',
                     ('planned_date_begin', '<=', self.date_start),
                     ('planned_date_end', '>=', self.date_end)])
                agenda_ids = self.env['agenda.agenda'].search(
                    [('user_ids', 'in', user), '|',
                     ('task_id', '!=', self.field_service_id.id),
                     ('task_id', '=', False),
                     '|',
                     '|',
                     '&',
                     ('date_start', '>=', self.date_start),
                     ('date_start', '<=', self.date_end),
                     '&',
                     ('date_end', '>=', self.date_start),
                     ('date_end', '<=', self.date_end),
                     '&',
                     ('date_start', '<=', self.date_start),
                     ('date_end', '>=', self.date_end)])
                if not task_ids and not agenda_ids:
                    self.is_resource_set_on_task = False
                    self.is_resource_set_on_agenda = False
                else:
                    if task_ids:
                        self.is_resource_set_on_task = True
                        break
                    else:
                        self.is_resource_set_on_task = False
                    if agenda_ids:
                        self.is_resource_set_on_agenda = True
                        break
                    else:
                        self.is_resource_set_on_agenda = False
        else:
            self.is_resource_set_on_task = False
            self.is_resource_set_on_agenda = False

    def return_check_resources_view(self):
        view_id = self.env.ref('custom_helpdesk.project_task_agenda_view')
        user_list = self.find_user_list()
        task_ids = self.env['project.task'].search(
            [('is_fsm', '=', True),
             ('planned_date_begin', '>=', self.date_start),
             ('planned_date_end', '<=', self.date_end),
             ('user_ids', 'in', user_list)])
        lines = []
        for line in task_ids:
            task_user_list = line.co_user_ids.ids
            task_user_list.append(line.user_id.id)
            for user in task_user_list:
                project_task_agenda_id = self.env['project.task.agenda'].search(
                    [('task_id', '=', line.id), ('user_id', '=', user),
                     ('date_start', '>=', line.planned_date_begin),
                     ('date_end', '<=', line.planned_date_end)])
                if project_task_agenda_id:
                    project_task_agenda_id.write({
                        'name': line.name,
                        'user_id': user,
                        'task_id': line.id,
                        'date_start': line.planned_date_begin,
                        'date_end': line.planned_date_end
                    })
                else:
                    res_id = self.env['project.task.agenda'].create({
                        'name': line.name,
                        'user_id': user,
                        'task_id': line.id,
                        'date_start': line.planned_date_begin,
                        'date_end': line.planned_date_end
                    })
                    lines.append(res_id.id)

        agenda_ids = self.env['agenda.agenda'].search(
            [('date_start', '>=', self.date_start),
             ('date_end', '<=', self.date_end),
             ('user_ids', 'in', user_list)])
        for agenda in agenda_ids:
            for user in agenda.user_ids:
                project_task_agenda_id = self.env['project.task.agenda'].search(
                    [('agenda_id', '=', agenda.id), ('user_id', '=', user.id),
                     ('date_start', '>=', agenda.date_start),
                     ('date_end', '<=', agenda.date_end)])
                if project_task_agenda_id:
                    project_task_agenda_id.write({
                        'user_id': user.id,
                        'name': agenda.reservation_reason.name,
                        'agenda_id': agenda.id,
                        'date_start': agenda.date_start,
                        'date_end': agenda.date_end
                    })
                else:
                    res_id = self.env['project.task.agenda'].create({
                        'user_id': user.id,
                        'name': agenda.reservation_reason.name,
                        'agenda_id': agenda.id,
                        'date_start': agenda.date_start,
                        'date_end': agenda.date_end
                    })
                    lines.append(res_id.id)

        return {
            'name': 'Available Resources',
            'type': 'ir.actions.act_window',
            'view_mode': 'gantt',
            'res_model': 'project.task.agenda',  # name of respective model,
            'views': [(view_id.id, 'gantt')],
            'target': 'new',
            'domain': [('date_start', '>=', self.date_start),
                       ('date_end', '<=', self.date_end),
                       ('user_id', 'in', user_list)]
        }

    def write(self, values):
        if values.get('user_id'):
            self.field_service_id.activity_unlink(
                ['custom_helpdesk.mail_activity_user_update'])
            note = "You are removed from the task."
            self.field_service_id.activity_schedule(
                'custom_helpdesk.mail_activity_user_removed',
                note=note,
                user_id=self.user_id.id)

        if values.get('stage_id'):
            new_stage_id = self.env['helpdesk.stage'].browse(
                [values['stage_id']])
            if new_stage_id.archive_ticket:
                self.active = False
            # this section is to allow moving tickets forward only
            if self.stage_id.sequence > new_stage_id.sequence:
                raise UserError(_("You can only move tickets forward"))

            # this section is to check whether the user have the premission of
            # moving from the selected ticket
            if self.stage_id.limited_users and not self.stage_id.only_notification:
                if self.env.user.id in self.stage_id.limited_users.ids or self.env.context.get(
                        'active_fs_ticket'):
                    # === ALLOW ===
                    pass

                else:
                    raise UserError(
                        _("You don't have permission to move the ticket to this"
                          " stage"))



            # this section is to check whether the new stage require full
            # resources
            if new_stage_id.require_full_resource and not self.resources_are_full:
                raise UserError(
                    _(f"This ticket can not be moved to {new_stage_id.name} stage because some resources are missing"))

            if new_stage_id.send_notification_to_spare_parts_responsible:
                if self.brand_id:
                    responsible_users = self.brand_id.spare_parts_user_ids.ids
                    activity_id = self.env['mail.activity'].search(
                        [('res_id', '=', self.id),
                         ('activity_type_id', '=', self.env.ref(
                             'custom_helpdesk.mail_activity_fs_ticket_move_out_of_the_stage_modality').id)])
                    activity_id.action_feedback(feedback="")
                    note = _(
                        "A new ticket has been moved to your stage: %s") % (
                               self.name)
                    for user in responsible_users:
                        self.activity_schedule(
                            'custom_helpdesk.mail_activity_fs_ticket_move_out_of_the_stage_modality',
                            note=note,
                            user_id=user)

        return super(CustomHelpDeskTicket, self).write(values)

    @api.constrains('name')
    def find_similar_tickets(self):
        """ Method to find similar helpdesk tickets."""
        for ticket in self:
            if ticket:
                ticket_id = self.env['helpdesk.ticket'].search(
                    [('sn', '=', ticket.sn), ('active', '=', True),
                     ('id', '!=', ticket.id),('stage_id.is_close', '!=', True)])
                ticket_names = ticket_id.mapped('name')
                listToStr = ' , '.join([elem for elem in ticket_names])
                ticket.similar_tickets = listToStr

    def compute_overlap_sn_trigger(self):
        self.env["helpdesk.ticket"].search([("stage_id", "not in", [4, 18, 19, 3])]).compute_overlap_sn()

    @api.depends('unit_id')
    def compute_overlap_sn(self):
        """ Method to show conflicted helpdesk tickets with same serial number."""
        for ticket in self:
            if ticket.unit_id:
                similar_tickets = self.env['helpdesk.ticket'].search(
                    [('sn', '=', ticket.sn), ('active', '=', True),
                     ('id', '!=', ticket._origin.id),
                     ('unit_id', '=', ticket.unit_id.id),
                     ('stage_id.is_close', '=', False)])
                if similar_tickets:
                    ticket.overlap_sn = True
                else:
                    ticket.overlap_sn = False
            else:
                ticket.overlap_sn = False

    def view_tickets_with_same_serial_number(self):
        """ Method to view tickets with same serial number """
        tickets = self.env['helpdesk.ticket'].search(
            [('sn', '=', self.sn), ('active', '=', True), ('id', '!=', self.id),
             ('stage_id.is_close', '!=', True)])
        if tickets:
            return {
                'type': 'ir.actions.act_window',
                'name': 'Similar Tickets',
                'view_type': 'form',
                'view_mode': 'kanban',
                'res_model': 'helpdesk.ticket',
                'views': [(False, 'kanban'), (False, 'list'), (False, 'form')],
                'domain': [('id', 'in', tickets.ids)],
                'target': 'current'
            }

    def search_by_sn(self):
        """ Method to search contract by serial number."""
        contract_line_id = self.env['contract.product'].search(
            [('sn', '=ilike', self.sn_search)],
            order="starting_date desc", limit=1)
        if len(contract_line_id) == 0:
            raise UserError(
                _(f"No Conrtact was found with for serial number {self.sn_search}"))
        else:
            self.unit_id = contract_line_id.id
            self.province_id = contract_line_id.site.site_province.id
            self.brand_id = contract_line_id.modality.id
            self.site_id = contract_line_id.site.id

    @api.constrains('date_start', 'date_end')
    def onsave_date_start_and_date_end(self):
        """  Method to change the start date and end date from the related field service when the task range updated
        on helpdesk ticket. """
        if self.field_service_id:
            if not self.env.context.get('is_onchange_task'):
                self.field_service_id.planned_date_begin = self.date_start
                self.field_service_id.planned_date_end = self.date_end
                agenda_id = self.env['agenda.agenda'].search(
                    [('task_id', '=', self.field_service_id.id)])
                agenda_id.date_start = self.date_start
                agenda_id.date_end = self.date_end

    @api.constrains('stage_id')
    def check_stage_service(self):
        for ticket in self:
            # Check if Service Report Was Created Before Moving to a stage that required service report
            if ticket.ticket_type_id.require_service_report:
                if ticket.stage_id.require_field_service and not ticket.field_service_id.service_report_id and ticket.ticket_type_id.name == 'Defect':
                    raise UserError(
                        _("The field service ticket needs to finish its cycle before moving this helpdesk ticket"))

            co_workers = [(4, user.id) for user in
                          ticket.resource_lines.mapped('user_ids')]
            co_vehicles = [(4, vehicle.id) for vehicle in
                           ticket.resource_lines.mapped('vehicle_ids')]
            # Auto create service report if the ticket is moved to an auto_create_field_service stage
            if ticket.stage_id.auto_create_field_service:
                if ticket.date_start and ticket.date_end and ticket.user_id:
                    if ticket.ticket_type_id.is_reported_by_required and not ticket.partner_id:
                        raise UserError(
                            _("Please enter the \"Report By\" Person"))
                    else:
                        project_id = self.env.ref('industry_fsm.fsm_project')
                        service_id = self.env['project.task'].create({
                            "name": f"FS - {ticket.name}",
                            "brand_id": ticket.brand_id.id,
                            "co_user_ids": co_workers,
                            "vehicle_ids": co_vehicles,
                            "planned_date_begin": ticket.date_start,
                            "date_deadline": ticket.date_end,
                            "is_fsm": True,
                            "description": ticket.description,
                            "user_ids": [(fields.Command.link(ticket.user_id.id))],
                            "project_id": project_id.id,
                            "partner_id": ticket.partner_id.id,
                            "related_helpdesk_ticket": ticket.id,
                            "is_contract_valid": ticket.contract_is_valid,
                            "province": ticket.province_id.id,
                            "serial_no_search": ticket.sn_search,
                            "maintenance_iq": ticket.new_maintenance_iq,
                        })
                        co_workers.append((4, ticket.user_id.id))
                        reservation_reason_id = self.env[
                            'reservation.reason'].search(
                            [('name', '=ilike', 'Field Service')])
                        if reservation_reason_id:
                            self.env['agenda.agenda'].create({
                                'date_start': ticket.date_start,
                                'date_end': ticket.date_end,
                                'user_ids': co_workers,
                                'task_id': service_id.id,
                                'reservation_reason': reservation_reason_id.id,
                            })

                        else:
                            reservation_reason_id = self.env[
                                'reservation.reason'].create({
                                'name': 'Field Service'
                            })
                            self.env['agenda.agenda'].create({
                                'date_start': ticket.date_start,
                                'date_end': ticket.date_end,
                                'user_ids': co_workers,
                                'task_id': service_id.id,
                                'reservation_reason': reservation_reason_id.id,
                            })
                        ticket.field_service_id = service_id.id
                        if ticket.parent_ticket.field_service_id:
                            ticket.parent_ticket.field_service_id.write({
                                'child_ids': [service_id.id],
                            })

                elif not ticket.user_id:
                    raise UserError(
                        _("Please select the reponsible user before moving the ticket"))
                else:
                    raise UserError(
                        _("Please fill the task range before moving the ticket"))

    def _get_default_resource(self):
        co_person_job_resource = self.env[
            'helpdedesk.resource.category'].search(
            [('name', '=', 'Co Person Job')], limit=1)
        return [
            (0, 0, {'categ_id': self.env.ref('itkan_helpdesk.data_enginner').id,
                    'qty': 0}),
            (0, 0,
             {'categ_id': self.env.ref('itkan_helpdesk.data_co_enginner').id,
              'qty': 0}),
            (0, 0,
             {'categ_id': self.env.ref('itkan_helpdesk.data_technicians').id,
              'qty': 0}),
            (0, 0, {'categ_id': self.env.ref('itkan_helpdesk.data_vehicles').id,
                    'qty': 0}),
            (0, 0, {'categ_id': co_person_job_resource.id,
                    'qty': 0}),
        ]


class CustomHelpDeskResource(models.Model):
    _inherit = "helpdedesk.resource"

    new_user_ids = fields.Many2many("res.users", compute='compute_users')
    user_ids = fields.Many2many("res.users",
                                domain="[('user_ids', 'in', new_user_ids)]")

    @api.depends('categ_id')
    def compute_users(self):
        """ Method to compute users based on category."""
        user_id = self.sudo().env['res.users']
        for rec in self:
            if rec.categ_id.name == 'Technicians' or rec.categ_id.name == 'Technician':
                users = user_id.search(
                    [('emp_id.new_divisions.name', '=', 'Technical'),
                     ('emp_id.job_id.name', 'ilike', 'Technician')])
            else:
                users = user_id.search([])
            rec.new_user_ids = users.ids

    def write(self, vals):
        if vals.get('user_ids'):
            user_ids = [value[1] for value in vals.get('user_ids')]
            for user in self.user_ids:
                if user.id not in user_ids:
                    self.helpdesk_ticket_id.field_service_id.activity_unlink(
                        ['custom_helpdesk.mail_activity_resource_update'])
                    note = "You are removed from the task."
                    self.helpdesk_ticket_id.field_service_id.activity_schedule(
                        'custom_helpdesk.mail_activity_resource_removed',
                        note=note,
                        user_id=user.id)
            users = self.env['res.users'].search(
                [('id', 'in', user_ids)]).mapped('name')
            user_names = ','.join(users)
            if self.user_ids:
                userss = ','.join(self.user_ids.mapped('name'))
                message = self.categ_id.name + " - Assigned Users : " + userss + " --> Assigned users : " + user_names
            else:
                message = self.categ_id.name + " - Assigned Users : " + user_names
            self.helpdesk_ticket_id.message_post(body=message)
        if vals.get('vehicle_ids'):
            vehicle_ids = [value[1] for value in vals.get('vehicle_ids')]
            vehicles = self.env['fleet.vehicle'].search(
                [('id', 'in', vehicle_ids)]).mapped('name')
            vehicle_names = ','.join(vehicles)
            if self.vehicle_ids:
                vehicless = ','.join(self.vehicle_ids.mapped('name'))
                message = self.categ_id.name + " -Assigned Vehicles : " + vehicless + "--> Assigned Vehicles : " + vehicle_names
            else:
                message = self.categ_id.name + " -Assigned Vehicles : " + vehicle_names
            self.helpdesk_ticket_id.message_post(body=message)
        return super(CustomHelpDeskResource, self).write(vals)


class CustomHelpDeskResourceCategory(models.Model):
    _inherit = "helpdedesk.resource.category"

    type = fields.Selection([('human', 'People'), ('vehicle', 'Vehicle')],
                            default='human', required=True)

#TODO : This class Must be removed after migration of custom_sales
class CustomResUsers(models.Model):
    _inherit = 'res.users'

    emp_id = fields.Many2one('hr.employee', string="Employee", store=True,
                             compute='_compute_company_emp_id')

    @api.depends('employee_ids')
    @api.depends_context('force_company')
    def _compute_company_emp_id(self):
        for user in self:
            user.emp_id = self.env['hr.employee'].search(
                [('id', 'in', user.employee_ids.ids),
                 ('company_id', '=', self.env.company.id)], limit=1)



class ExtendProjectTask(models.Model):
    _inherit = "project.task"
    # TODO delete this field declaration after installation of custom_industry_fsm
    maintenance_iq = fields.Char('maintenance_iq')

    def _get_default_stage_id(self):
        """ Gives default stage_id """
        project_id = self.env.context.get('default_project_id')
        if not project_id:
            return False
        return self.stage_find(project_id, [('fold', '=', False)])

    related_helpdesk_ticket = fields.Many2one("helpdesk.ticket",
                                              string="Related Helpdesk Ticket",
                                              ondelete='cascade')

    is_contract_valid = fields.Boolean(string="Is contract valid",
                                       related='related_helpdesk_ticket.contract_is_valid')
    is_contract_in_warranty = fields.Boolean(string="Is contract in Warranty",
                                             related='related_helpdesk_ticket.is_contract_in_warranty')

    province = fields.Many2one('contract.province', string="Province",
                               related='related_helpdesk_ticket.province_id',
                               readonly=False)
    partner_id = fields.Many2one('res.partner',
                                 string='Customer', recursive=True, tracking=True, compute='_compute_partner_id',
                                 related='related_helpdesk_ticket.partner_id',
                                 store=True, readonly=False,
                                 domain="['|', ('company_id', '=?', company_id), ('company_id', '=', False)]", )

    brand_id = fields.Many2one('contract.modality', string="Modality",
                               related='related_helpdesk_ticket.brand_id',
                               readonly=False)
    sn = fields.Char("SN Number", related="related_helpdesk_ticket.sn",
                     readonly=False)
    serial_no_search = fields.Char("Search By Serial Number", readonly=False)
    site_id = fields.Many2one('contract.site', string="Site",
                              related="related_helpdesk_ticket.site_id")
    allowed_stages = fields.Many2many('project.task.type',
                                      related='related_helpdesk_ticket.ticket_type_id.allowed_fs_stages')
    stage_id = fields.Many2one('project.task.type', string='Stage',
                               ondelete='restrict', tracking=True, index=True,
                               default=_get_default_stage_id,
                               group_expand='_read_group_stage_ids',
                               domain="[('project_ids', '=', project_id),('id','in',allowed_stages)]",
                               copy=False)

    service_report_docs = fields.Many2many(comodel_name="ir.attachment",
                                           relation="attachement_task_service_report_rel",
                                           column1="task_id",
                                           column2="attachment_id",
                                           string="Service Report Document"
                                           )
    is_fsm = fields.Boolean(related='project_id.is_fsm',
                            search='_search_is_fsm', store=True)
    ticket_type_id = fields.Many2one('helpdesk.ticket.type',
                                     string="Ticket Type",
                                     related='related_helpdesk_ticket.ticket_type_id')
    active = fields.Boolean(default=True, related='related_helpdesk_ticket.active')
    is_show_product_cart = fields.Boolean(string="Show Product Cart", related="ticket_type_id.is_show_product_cart")
    can_edit_task_range = fields.Boolean(string="Edit Task Range", related="ticket_type_id.can_edit_task_range")

    @api.model
    def create(self, vals):
        res = super(ExtendProjectTask, self).create(vals)
        service_report_docs = res.mapped('service_report_docs')
        service_report_docs.write({
            'res_id': res.id,
        })
        return res

    @api.onchange('planned_date_begin','date_deadline')
    def onchange_planned_date_begin(self):
        ticket_id = self.related_helpdesk_ticket
        ticket_id.with_context(is_onchange_task = True).date_start = self.planned_date_begin
        ticket_id.with_context(
            is_onchange_task=True).date_end = self.date_deadline

    def write(self, values):
        old_stage = self.stage_id
        if old_stage.limited_users and values.get("stage_id"):
            if self.env.user in old_stage.limited_users:
                pass
            else:
                raise UserError(_("You dont have access to move from this stage."))
        if 'description' in values.keys():
            cleanr = re.compile('<.*?>')
            cleantext = re.sub(cleanr, '', values["description"])
            self.related_helpdesk_ticket.description = cleantext

        if 'stage_id' in values.keys():
            new_stage_id = self.env['project.task.type'].browse(
                [values['stage_id']])
            if self.stage_id.confirm_sale_order_if_contract_in_warranty:
                if self.is_contract_in_warranty:
                    # sale_id = self.env['sale.order'].browse(
                    #     self.sudo().sale_order_id.id)
                    sale_id = self.sudo().sale_order_id
                    if sale_id.state == "draft":
                        sale_id.sudo().action_confirm()
            if self.stage_id.confirm_sale_order_if_contract_is_expired:
                if not self.is_contract_in_warranty:
                    # sale_id = self.env['sale.order'].browse(
                    #     self.sudo().sale_order_id.id)
                    sale_id = self.sudo().sale_order_id
                    if sale_id.state == "draft":
                        sale_id.sudo().action_confirm()
            if self.stage_id.check_product_cart:
                if self.env.user.id in self.stage_id.limited_users.ids or self.env.user.id in self.brand_id.user_ids.ids:
                    pass
                else:
                    if self.material_line_product_count:
                        raise UserError(
                            _("You need approval for products in the cart."))

            if self.stage_id.sequence > new_stage_id.sequence:
                raise UserError(_("You can only move tickets forward"))

            elif new_stage_id.move_to_stage_limited_users.ids:
                if self.env.user.id in new_stage_id.move_to_stage_limited_users.ids:
                    pass
                else:
                    raise UserError(
                        _("You don't have access to move this task"))

            elif self.related_helpdesk_ticket.ticket_type_id.allowed_fs_stages:
                if values[
                    'stage_id'] in self.related_helpdesk_ticket.ticket_type_id.allowed_fs_stages.ids:
                    super(ExtendProjectTask, self).write(values)
                else:
                    raise UserError(
                        _("You can't move to this stage for the help desk type ' %s' ") % (
                            self.related_helpdesk_ticket.ticket_type_id.name))
            if old_stage.out_of_this_stage_alarm_for_modality:
                modality_id = self.brand_id
                users = [user.id for user in modality_id.user_ids]

                for user in users:
                    note = _(
                        "A new ticket has been moved to your stage: %s") % (
                               self.name)
                    activity_id = self.env['mail.activity'].search(
                        [('res_id', '=', self.id),
                         ('activity_type_id', '=', self.env.ref(
                             'custom_helpdesk.mail_activity_fs_ticket_move_out_of_the_stage').id)])
                    activity_id.action_feedback(feedback="")
                    self.activity_schedule(
                        'custom_helpdesk.mail_activity_fs_ticket_move_out_of_the_stage',
                        note=note,
                        user_id=user)

            if old_stage.out_of_this_stage_alarm_for_resources:
                resource_users = [self.user_ids[0].id]
                resources = self.co_user_ids.ids
                resource_users = list(set(resource_users + resources))
                activity_id = self.env['mail.activity'].search(
                    [('res_id', '=', self.id),
                     ('activity_type_id', '=', self.env.ref(
                         'custom_helpdesk.mail_activity_fs_ticket_move_out_of_the_stage_resources').id)])
                note = _("A new ticket has been moved to your stage: %s") % (
                    self.name)
                activity_id.action_feedback(feedback="")
                for user in resource_users:
                    self.activity_schedule(
                        'custom_helpdesk.mail_activity_fs_ticket_move_out_of_the_stage_resources',
                        note=note,
                        user_id=user)
            if new_stage_id.send_notification_to_spare_parts_responsible:
                if self.brand_id:
                    responsible_users = self.brand_id.spare_parts_user_ids.ids
                    activity_id = self.env['mail.activity'].search(
                        [('res_id', '=', self.id),
                         ('activity_type_id', '=', self.env.ref(
                             'custom_helpdesk.mail_activity_fs_ticket_move_out_of_the_stage_modality').id)])
                    activity_id.action_feedback(feedback="")
                    note = _(
                        "A new ticket has been moved to your stage: %s") % (
                               self.name)
                    for user in responsible_users:
                        self.activity_schedule(
                            'custom_helpdesk.mail_activity_fs_ticket_move_out_of_the_stage_modality',
                            note=note,
                            user_id=user)
        super(ExtendProjectTask, self).write(values)

    @api.constrains('stage_id')
    def send_users_notificaiton(self):
        """ Method to send user notifications. """
        if self.stage_id and self.stage_id.name.lower() == 'new':
            pass
        else:
            helpdesk_activity_id = self.env['mail.activity'].search(
                [('res_id', '=', self.id),
                 ('activity_type_id', '=', self.env.ref(
                     'custom_helpdesk.mail_activity_helpdesk_ticket_move').id)])
            if helpdesk_activity_id:
                helpdesk_activity_id.action_feedback(feedback="")

        activity_id = self.env['mail.activity'].search(
            [('res_id', '=', self.id),
             ('activity_type_id', '=', self.env.ref(
                 'custom_helpdesk.mail_activity_fs_ticket_move').id)])
        activity_id.action_feedback(feedback="")
        users = []
        if self.stage_id and (self.stage_id.name.lower() == 'done' or self.stage_id.name.lower() == 'offer refused'):
            pass
        else:
            if self.stage_id.modality_stage:
                modality_id = self.brand_id
                users = [user.id for user in modality_id.user_ids]

            elif self.stage_id.limited_users and not self.stage_id.is_not_send_notification:
                users = [user.id for user in self.stage_id.limited_users]

            if self.stage_id.is_the_users_to_be_notified:
                users.append(self.user_id[0].id)
                resources = self.co_user_ids.ids
                users = list(set(users + resources))

            # =============================

            if users:
                note = _("A new ticket has been moved to your stage: %s") % (
                    self.name)
                for user in users:
                    self.activity_schedule(
                        'custom_helpdesk.mail_activity_fs_ticket_move',
                        note=note,
                        user_id=user)

        if self.stage_id and ( self.stage_id.name.lower() == 'modality approval' or self.stage_id.name.lower() == 'out of contracts customer Aapproval'):
            helpdesk_stage = self.env['helpdesk.stage'].search(
                [('name', '=', 'Pending Approval')])

    @api.constrains('related_helpdesk_ticket')
    def send_notification_to_co_workers(self):
        """ Method to send notification to co-persons"""
        if self.related_helpdesk_ticket:
            users = [user.id for user in self.co_user_ids]
            users.append(self.related_helpdesk_ticket.user_id.id)
            for user in users:
                note = "You have been assigned the following task"
                self.activity_schedule(
                    'custom_helpdesk.mail_activity_helpdesk_ticket_move',
                    note=note,
                    user_id=user)

    def stage_find(self, section_id, domain=[], order='sequence'):
        """ Override of the base.stage method
            Parameter of the stage search taken from the lead:
            - section_id: if set, stages must belong to this section or
              be a default stage; if not set, stages must be default
              stages
        """
        # collect all section_ids
        section_ids = []
        if section_id:
            section_ids.append(section_id)
        section_ids.extend(self.mapped('project_id').ids)
        search_domain = []
        if section_ids:
            search_domain = [('|')] * (len(section_ids) - 1)
            for section_id in section_ids:
                search_domain.append(('project_ids', '=', section_id))
        if self.allowed_stages:
            if self.related_helpdesk_ticket.ticket_type_id.is_to_hide_other_stages:
                search_domain.append(('id', 'in', self.allowed_stages))

        search_domain += list(domain)
        # perform search, return the first found
        return self.env['project.task.type'].search(search_domain, order=order,
                                                    limit=1).id

    def search_by_serial_no(self):
        """ Method to search contract by serial number."""
        contract_line_id = self.env['contract.product'].search(
            [('sn', '=ilike', self.serial_no_search)],
            order="starting_date desc", limit=1)
        if len(contract_line_id) == 0:
            raise UserError(
                _(f"No Contract was found with for serial number {self.serial_no_search}"))
        else:
            if self.related_helpdesk_ticket:
                self.related_helpdesk_ticket.province_id = contract_line_id.site.site_province.id
                self.related_helpdesk_ticket.brand_id = contract_line_id.modality.id
                self.related_helpdesk_ticket.sn_search = contract_line_id.sn
                self.related_helpdesk_ticket.search_by_sn()
                self.related_helpdesk_ticket.unit_id = contract_line_id.id
                self.related_helpdesk_ticket.contract_id = contract_line_id.contract_id.id
                self.related_helpdesk_ticket.sn = contract_line_id.sn
            self.name = f"FS - {self.related_helpdesk_ticket.name}"
            self.sn = contract_line_id.sn
            self.province = contract_line_id.site.site_province.id
            self.brand_id = contract_line_id.modality.id

    def action_field_service_main_task(self):
        """ Return action of task"""
        if self.parent_id:
            return {
                "name": "Main Task",
                "type": "ir.actions.act_window",
                "res_model": "project.task",
                "views": [
                    [self.env.ref('industry_fsm.project_task_view_form').id,
                     "form"],
                ],
                "res_id": self.parent_id.id,
            }


    def action_field_service_subtask(self):
        """ Return action for subtask."""

        return {
            "type": "ir.actions.act_window",
            "res_model": "project.task",
            "views": [[False, "kanban"],
                      [self.env.ref('industry_fsm.project_task_view_form').id,
                       "form"],
                      [False, "list"]],
            "domain": [("id", "in", self.child_ids.ids)],
            "context": dict(self._context, create=False),
            "name": "SUB FST",
        }

    @api.constrains('stage_id')
    def check_stage_change(self):
        """ Method to create service report."""
        # creating service Report
        if self.stage_id.auto_create_service_report and self.is_fsm and self.related_helpdesk_ticket and not self.related_helpdesk_ticket.child_ticket and self.related_helpdesk_ticket.ticket_type_id.require_service_report:
            if self.co_user_ids:
                co_persons = ' / '.join([p.name for p in self.co_user_ids])
            else:
                co_persons = ''
            ticket_id = self.related_helpdesk_ticket
            cars_names = ticket_id.resource_lines.mapped('vehicle_ids.name')
            cars_sting = ', '.join(cars_names)
            if ticket_id.ticket_type_id.name == 'Preventive maintenance':
                service_report_id = self.env['service.report'].create({
                    'task_number': '#' + str(ticket_id.id),
                    'modality': ticket_id.brand_id.id,
                    'province': ticket_id.province_id.id,
                    't_type': 'job',
                    'reported_by': ticket_id.site_id.site_name,
                    'car': cars_sting,
                    'contract': ticket_id.contract_id.id,
                    'site': ticket_id.site_id.id,
                    'sn': ticket_id.sn,
                    'unit': ticket_id.unit_id.product_char if ticket_id.unit_id.product_char else ticket_id.unit_id.product_id.name,
                    'description': ticket_id.description if ticket_id.description else '',
                    'resource': co_persons,
                    'engineer': self.user_ids[0].partner_id.id,
                    'task_id': self.id,
                    'job_number': ticket_id.job_number,
                    'done_desc': ticket_id.pm_workdone_description,
                })
            else:

                service_report_id = self.env['service.report'].create({
                    'task_number': '#' + str(ticket_id.id),
                    'modality': ticket_id.brand_id.id,
                    'province': ticket_id.province_id.id,
                    't_type': 'job',
                    'reported_by': ticket_id.site_id.site_name,
                    'car': cars_sting,
                    'contract': ticket_id.contract_id.id,
                    'site': ticket_id.site_id.id,
                    'sn': ticket_id.sn,
                    'unit': ticket_id.unit_id.product_char if ticket_id.unit_id.product_char else ticket_id.unit_id.product_id.name,
                    'description': ticket_id.description if ticket_id.description else '',
                    'resource': co_persons,
                    'engineer': self.user_ids[0].partner_id.id,
                    'task_id': self.id,
                    'job_number': ticket_id.job_number,
                })

            self.service_report_id = service_report_id
            ticket_id.service_report_id = service_report_id

        # moving related helpdesk ticket to related stage
        if self.stage_id.helpdesk_stage_id and self.is_fsm and self.related_helpdesk_ticket and not self.related_helpdesk_ticket.child_ticket:
            ticket_id = self.related_helpdesk_ticket
            ticket_id.with_context(
                active_fs_ticket=True).stage_id = self.stage_id.helpdesk_stage_id.id

        # sending notification
        if (self.stage_id.modality_stage and self.related_helpdesk_ticket) or (
                self.stage_id.limited_users):
            users = []
            modality_id = self.related_helpdesk_ticket.brand_id
            msg_body = 'Dear '

            if modality_id and modality_id.user_ids and self.stage_id.modality_stage:
                users = [user.partner_id.id for user in modality_id.user_ids]
                for user in modality_id.user_ids:
                    msg_body += Markup(f'<a href="#" data-oe-model="res.users" data-oe-id="{user.id}">{user.name}</a>, ')

            elif self.stage_id.limited_users and not self.stage_id.is_not_send_notification:
                users = [user.partner_id.id for user in
                         self.stage_id.limited_users]
                for user in self.stage_id.limited_users:
                    msg_body += Markup(f'<a href="#" data-oe-model="res.users" data-oe-id="{user.id}">{user.name}</a>, ')

            # ==============================
            view_id = self.env.ref("project.view_task_form2")
            if users:
                msg_body = msg_body[:-2] + Markup(f' A new fields service ticket is waiting for you approval:\
                         <a href="#" data-oe-model="project.task" data-oe-id="{self.id}" data-oe-view="{view_id.id}" data-oe-view-ref="{view_id.id}" data-oe-view_ref="{view_id.id}">{self.display_name}</a>')
                self.message_post(
                    body=msg_body,
                    message_type='notification',
                    subtype_xmlid='mail.mt_comment',
                    partner_ids=users)
