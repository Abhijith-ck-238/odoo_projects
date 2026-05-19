from odoo import fields, models, api, _
from odoo.exceptions import UserError


class GeneralLetterTicket(models.Model):
    _name = "general.letter.ticket"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = "General Letter Ticket"

    def _get_default_stage_id(self):
        return self.env['general.letter.stage'].search([], order='sequence',
                                                       limit=1)

    name = fields.Char(string="Ticket Description", tracking=True)
    stage_id = fields.Many2one('general.letter.stage', string="Stage",
                               copy=False,
                               default=_get_default_stage_id,
                               group_expand='_read_group_expand_full',
                               tracking=True, store=True)
    letter_type_id = fields.Many2one('general.letter.type',
                                     string='Letter Type', required=True)
    color = fields.Integer(string='Color Index')
    active = fields.Boolean(default=True)
    company_id = fields.Many2one('res.company', string='Company',
                                 required=True,
                                 default=lambda self: self.env.company)
    contract_id = fields.Many2one('contract.contract', string="Contract",
                                  required=True)
    attachment_ids = fields.Many2many('ir.attachment', string="Attachments")
    modality_id = fields.Many2one('contract.modality', string="Modality",
                                  required=True)
    approval_letter = fields.Many2many('ir.attachment',
                                       string="Approval Letter",
                                       relation="rel_attachment_approval_general_letter")

    @api.model
    def _read_group_stage_ids(self, stages, domain):
        return self.env['general.letter.stage'].search([])

    def write(self, vals):
        if vals.get('stage_id'):
            new_stage_id = self.env["general.letter.stage"].browse(
                vals.get('stage_id'))
            if self.stage_id:
                if new_stage_id:
                    if self.env.user.id not in self.stage_id.move_from_user_ids.ids:
                        raise UserError(
                            _("You don't have access to move the letter ticket from this stage."))
                    if self.env.user.id not in new_stage_id.move_to_user_ids.ids:
                        raise UserError(
                            _("You don't have access to move the letter ticket to this stage."))
            if new_stage_id.send_activity_for_modality_manager:
                users = self.modality_id.user_ids
                self.activity_ids.action_done()
                for user in users:
                    if user.id in new_stage_id.move_from_user_ids.ids:
                        self.env['mail.activity'].sudo().create({
                            'display_name': 'Letter Stage Changed',
                            'summary': 'Letter Stage Changed',
                            'note': "The letter is moved from the stage " + self.stage_id.name + "to the stage " + new_stage_id.name + ".",
                            'date_deadline': fields.datetime.now(),
                            'user_id': int(user.id),
                            'res_id': self.id,
                            'res_model_id': self.env['ir.model'].sudo().search(
                                [('model', '=', 'general.letter.ticket')],
                                limit=1).id,
                            'activity_type_id': self.env.ref(
                                'custom_general_letters.mail_activity_general_letter_ticket').id,
                        })
            else:
                users = new_stage_id.move_from_user_ids
                self.activity_ids.action_done()
                for user in users:
                    self.env['mail.activity'].sudo().create({
                        'display_name': 'Letter Stage Changed',
                        'summary': 'Letter Stage Changed',
                        'note': "The letter is moved from the stage " + self.stage_id.name + "to the stage " + new_stage_id.name + ".",
                        'date_deadline': fields.datetime.now(),
                        'user_id': int(user.id),
                        'res_id': self.id,
                        'res_model_id': self.env['ir.model'].sudo().search(
                            [('model', '=', 'general.letter.ticket')],
                            limit=1).id,
                        'activity_type_id': self.env.ref(
                            'custom_general_letters.mail_activity_general_letter_ticket').id,
                    })
            if new_stage_id.require_approval_letter and not self.approval_letter:
                raise UserError(
                    _("You need to upload Approval Letter before moving the task to this stage."))

        return super(GeneralLetterTicket, self).write(vals)

    @api.model
    def create(self, vals):
        res = super(GeneralLetterTicket, self).create(vals)
        attachment_ids = res.mapped('attachment_ids')
        approval_letter = res.mapped('approval_letter')
        attachment_ids.write({
            'res_id': res.id,
        })
        approval_letter.write({
            'res_id': res.id,
        })
        if vals.get('stage_id'):
            new_stage_id = self.env["general.letter.stage"].browse(
                vals.get('stage_id'))
            if new_stage_id.send_activity_for_modality_manager:
                users = self.modality_id.user_ids
                for user in users:
                    self.env['mail.activity'].sudo().create({
                        'display_name': 'Letter Stage Changed',
                        'summary': 'Letter Stage Changed',
                        'note': "The letter is moved to the stage " + new_stage_id.name + ".",
                        'date_deadline': fields.datetime.now(),
                        'user_id': int(user.id),
                        'res_id': res.id,
                        'res_model_id': self.env['ir.model'].sudo().search(
                            [('model', '=', 'general.letter.ticket')],
                            limit=1).id,
                        'activity_type_id': self.env.ref(
                            'custom_general_letters.mail_activity_general_letter_ticket').id,
                    })
            else:
                users = new_stage_id.move_from_user_ids
                for user in users:
                    self.env['mail.activity'].sudo().create({
                        'display_name': 'Letter Stage Changed',
                        'summary': 'Letter Stage Changed',
                        'note': "The letter is moved to the stage " + new_stage_id.name + ".",
                        'date_deadline': fields.datetime.now(),
                        'user_id': int(user.id),
                        'res_id': res.id,
                        'res_model_id': self.env['ir.model'].sudo().search(
                            [('model', '=', 'general.letter.ticket')],
                            limit=1).id,
                        'activity_type_id': self.env.ref(
                            'custom_general_letters.mail_activity_general_letter_ticket').id,
                    })
        return res
