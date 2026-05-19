# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import models, fields


class View(models.Model):
    _inherit = "ir.ui.view"

    def update_using_name(self,activate = False):
        # Define the views you want to activate with their module and name
        views_to_activate = [{'module': 'custom_pledges', 'name': 'pledge.ticket.kanban'},
                             {'module': 'custom_lower_ks', 'name': 'lower.ks.ticket.kanban'},
                             # {'module': 'custom_expense', 'name': 'crossovered.budget.view.form.inherit'},
                             {'module': 'product_bundle_pack', 'name': 'product.product.pack'},
                             {'module': 'leave_approver', 'name': 'hr.leave.type.form'},
                             {'module': 'leave_approver', 'name': 'hr.leave.view.form.manager'},
                             {'module': 'leave_approver', 'name': 'hr.leave.form'},
                             {'module': 'custom_project', 'name': 'project.project'},
                             {'module': 'custom_project', 'name': 'project.project'},
                             {'module': 'access_units', 'name': 'access_unit_product_inherit.form.2'},
                             {'module': 'access_units', 'name': 'product.product.kanban.access.units'},
                             {'module': 'itkan_offering', 'name': 'res.company.form.offer'},
                             {'module': 'hr_expense_advance_clearing', 'name': 'hr.expense.form'},
                             {'module': 'hr_expense_advance_clearing', 'name': 'view.hr.expense.sheet.form'},
                             {'module': 'itkan_fleet_customization', 'name': 'fleet_vehicle_inh.form'},
                             {'module': 'itkan_fleet_customization', 'name': 'fleet_vehicle_inh.kanban'},
                             {'module': 'itkan_helpdesk', 'name': 'helpdesk_inh.form'},
                             {'module': 'itkan_helpdesk', 'name': 'helpdesk.stage.tree.itkan'},
                             {'module': 'itkan_helpdesk', 'name': 'itkan.helpdesk.ticket.kanban'},
                             {'module': 'al-itkan', 'name': 'ITK_HR_APPL'},
                             {'module': 'al-itkan', 'name': 'ITK_Product'},
                             {'module': 'al-itkan', 'name': 'ITK_employee'},
                             {'module': 'custom_hr_expense_advance_clearng', 'name': 'hr.expense.inherit'},
                             {'module': 'custom_timeoff', 'name': 'hr.leave.type.extend.form'},
                             {'module': 'custom_timeoff', 'name': 'hr.leave.extend.form'},
                             {'module': 'custom_sales_team', 'name': 'sales.team.form.inherit'},
                             {'module': 'custom_helpdesk', 'name': 'helpdesk.ticket'},
                             {'module': 'industry_fsm_report', 'name': 'project.task.kanban.fsm.report'},
                             {'module': 'custom_helpdesk', 'name': 'agenda.agenda.tree'},
                             {'module': 'custom_helpdesk', 'name': 'agenda.agenda.form'},
                             {'module': 'custom_helpdesk', 'name': 'helpdesk.ticket.kanban.add.contract.status'},
                             {'module': 'custom_helpdesk','name': 'project.task.kanban.fsm.add.contract_status'},
                             {'module': 'custom_training', 'name': 'training.ticket.kanban'},
                             {'module': 'custom_fleet', 'name': 'fleet.vehicle.kanban.inherit'},
                             {'module': 'rfid_connector', 'name': 'stock.picking.form.view.inherit'},
                             {'module': 'custom_itkan_project', 'name': 'itkan.project.kanban'},
                             {'module': 'custom_letters', 'name': 'letter.ticket.kanban'},
                             {'module': 'custom_fleet', 'name': 'fleet.vehicle.kanban.inherit'},
                             {'module': 'custom_general_letters', 'name': 'general.letter.ticket.kanban'},
                             {'module': 'hr_recruitment', 'name': 'applicant.get.refuse.reason.form'},
                             {'module': 'hr_expense', 'name': 'hr.expense.sheet.form'},
                             {'module': 'custom_training', 'name': 'res.config.settings.view.form.inherit.training'},
                             {'module': 'custom_recruitment','name': 'res.config.settings.view.form.inherit.custom.recruitment'},
                             {'module': 'studio_customization','name': 'Odoo Studio: offering_po_footer customization'},
                             {'module': 'studio_customization','name': 'Odoo Studio: helpdesk.ticket.form customization'},
                             {'module': 'studio_customization', 'name': 'Odoo Studio: Contracts Form customization'},
                             {'module': 'studio_customization','name': 'Odoo Studio: project.task.kanban.fsm customization'},
                             {'module': 'studio_customization','name': 'Odoo Studio: Default form view for service.report.company customization'},
                             {'module': 'studio_customization','name': 'Odoo Studio: Jobs - Recruitment Form customization'},
                             {'module': 'studio_customization','name': 'Odoo Studio: project.task.tree.fsm customization'},
                             {'module': 'studio_customization','name': 'Odoo Studio: agenda.agenda.form customization'},
                             {'module': 'studio_customization','name': 'Odoo Studio: agenda.agenda.tree customization'},
                             {'module': 'studio_customization','name': 'Odoo Studio: Default gantt view for agenda.agenda customization'},
                             {'module': 'studio_customization','name': 'Odoo Studio: hr.leave.view.form customization'},
                             {'module': 'studio_customization','name': 'Odoo Studio: preventive.maintainence.tree customization'},
                             {'module': 'studio_customization','name': 'Odoo Studio: fleet.project.task.list customization'},
                             {'module': 'studio_customization','name': 'Odoo Studio: itkan.project.kanban customization'},
                             {'module': 'studio_customization', 'name': 'Odoo Studio: hr.employee.tree customization'},
                             {'module': 'studio_customization','name': 'Odoo Studio: hr.expense.sheet.view.search customization'},
                             {'module': 'custom_helpdesk', 'name': 'agenda.gantt.view.extend'},
                             {'module': 'access_units', 'name': 'access_unit_product_inherit.form.2'},
                             {'module': 'custom_sales', 'name': 'stock.picking.inherit'},
                             {'module': 'custom_hr_expense_advance_clearng', 'name': 'hr.expense.sheet.inherit'},
                             {'module': 'offering_configuration','name': 'product.template.product_name_without_spaces'},
                             {'module': 'custom_helpdesk', 'name': 'res.config.settings.view.form.inherit.helpdesk'},
                             {'module': 'custom_contract', 'name': 'contract.product.search'},
                             {'module': 'custom_purchase', 'name': 'view.move.form.inherit.custom.purcahse'},
                             {'module': 'custom_logistcs', 'name': 'view.move.form.inherit.custom.logistcs'},
                             {'module': 'studio_customization','name': 'Odoo Studio: product.template.product.form customization'},
                             {'module': 'studio_customization','name': 'Odoo Studio: contract.product.search customization'},
                             {'module': 'studio_customization','name': 'Odoo Studio: sale.order.form customization'},
                             {'module': 'studio_customization','name': 'partner.view.buttons'},
                             {'module': 'account','name': 'res.partner.property.form.inherit'},
                             {'module': 'purchase','name': 'res.partner.purchase.property.form.inherit'},
                             {'module': 'custom_sales','name': 'sale_order_inherits_form'},
                             {'module': 'custom_sales','name': 'sale order'},
                             {'module': 'custom_tac_ks','name': 'tac.ks.ticket.kanban'},
                             {'module': 'studio_customization','name': 'Odoo Studio: project.task.form customization'},
                             {'module': 'studio_customization','name': 'Odoo Studio: helpdesk.ticket.kanban customization'},
                             {'module': 'custom_fleet','name': 'fleet.project.task.list'},
                             {'module': 'al-itkan','name': 'ITK_Employee'},
                             {'module': 'custom_equipment','name': 'hr.employee.view.form.inherit'},
                             {'module': 'custom_recruitment','name': 'hr_applicant.view.form.inherit'},
                             {"name": 'sale_stock_report_invoice_document_proforma', "module": 'account_move'},
                             {"name": 'sale order', "module": 'custom_sales'}
                             ]
        views_to_archive =[
            {'name': 'res.users.form.session', 'module': 'odoo_user_login_security'},
            {'name': 'res.users.preferences.form', 'module': 'odoo_user_login_security'},
            {'name': 'Adding Page', 'module': 'odoo_user_login_security'},
            {'name': 'service_report_template_inherit', 'module': 'custom_service_reports'},
            {'name': 'service_report_template_inherit_1', 'module': 'custom_service_reports'},
            {'name': 'Odoo Studio: analytic.analytic.account.form customization', 'module': 'studio_customization'},
            {'name': 'Odoo Studio: stock.picking.form customization', 'module': 'studio_customization'},
            {'name': 'Odoo Studio: hr.employee.form customization', 'module': 'studio_customization'},
            {'name': 'Odoo Studio: hr.holidays.filter customization', 'module': 'studio_customization'},
            {'name': 'Odoo Studio: agenda.gantt.view customization', 'module': 'studio_customization'},
            {'name': 'Odoo Studio: training.ticket.kanban customization', 'module': 'studio_customization'},
            {'name': 'Odoo Studio: hr.holidays.view.tree customization', 'module': 'studio_customization'},
            {'name': 'expense payment move form', 'module': 'custom_hr_expense_advance_clearng'},
            {'name': 'expense payment move tree', 'module': 'custom_hr_expense_advance_clearng'},
            {'name': 'account.analytic.account.view.form.inherit.custom.expense', 'module': 'custom_expense'},
            {'name': 'hr.expense.sheet.form.inherit', 'module': 'custom_expense'},
            {'name': 'budget.analytic.view.tree.expense', 'module': 'custom_expense'},
            {'name': 'crossovered.budget.view.form.inherit', 'module': 'custom_expense'},
            {'name': 'budget.analytic.kanban.inherit', 'module': 'custom_expense'},
            {'name': 'Extend Budget line', 'module': 'custom_expense'},
            {'name': 'hr.expensenses.config.settings.view.form.inherit', 'module': 'custom_expense'},
            {'name': 'hr.employee.view.form.budget', 'module': 'custom_expense'},
            {'name': 'hr.expense.sheet.list.inherit', 'module': 'custom_expense'},
            {'name': 'res.config.settings.view.form.inherit.custom.expense', 'module': 'custom_expense'},
            {'name': 'expense account move', 'module': 'custom_hr_expense_advance_clearng'},
            {'name': 'expense account move tree', 'module': 'custom_hr_expense_advance_clearng'},
            {'name': 'expense.account.analytic.account.kanban', 'module': 'custom_hr_expense_advance_clearng'},
            {'name': 'hr.expense.sheet.inherit', 'module': 'custom_hr_expense_advance_clearng'},
            {'name': 'hr.expense.inherit', 'module': 'custom_hr_expense_advance_clearng'},
            {'name': 'account.analytic.account.inherit', 'module': 'custom_hr_expense_advance_clearng'},
            {'name': 'account.analytic.account.inherit.tree', 'module': 'custom_hr_expense_advance_clearng'},
            {'name': 'account.analytic.line.inherit', 'module': 'custom_hr_expense_advance_clearng'},
            {'name': 'account.analytic.line.tree.inherit', 'module': 'custom_hr_expense_advance_clearng'},
            {'name': 'hr.expense.list.inherit', 'module': 'custom_hr_expense_advance_clearng'},
            {'name': 'hr.expense.view.form.inherit.custom.fields', 'module': 'custom_hr_expense_advance_clearng'},
            {'name': 'account.analytic.tag.list', 'module': 'hr_expense_advance_clearing'},
            {'name': 'account.analytic.tag.form', 'module': 'hr_expense_advance_clearing'},
            {'name': 'hr.expense.form', 'module': 'hr_expense_advance_clearing'},
            {'name': 'view.hr.expense.sheet.form', 'module': 'hr_expense_advance_clearing'},
            {'name': 'hr.expense.view.form.inherit.documents.hr.expense', 'module': 'documents_hr_expense'},
            {'name': 'Remove Employee Access Groups', 'module': ''},
            {'name': 'hr.expense.form.inherit.sale.expense', 'module': 'sale_expense'},
            {'name': 'hr.expense.list.inherit.sale.expense', 'module': 'sale_expense'},
            {'name': 'hr.expense.sheet.form.inherit.sale.expense', 'module': 'sale_expense'},
            {'name': 'hr_expense_sheet.form', 'module': 'account_contracts_relation'},
            {'name': 'hr.expense.sheet.form.alitkan', 'module': 'al-itkan'},
            {'name': 'view.hr.expense.sheet.form.inherit.training', 'module': 'custom_training'},
            {'name': 'hr.expense.sheet.view.form.inherit.sale.expense', 'module': 'sale_expense'},
            {'name': 'Odoo Studio: hr.expense.sheet.tree customization', 'module': 'studio_customization'},
            {'name': 'res.config.settings.view.form.inherit.all.in.one.whatsapp.integration', 'module': 'all_in_one_whatsapp_integration'},
            {'name': 'mail.template.view.form.inherit.all.in.one.whatsapp.integration', 'module': 'all_in_one_whatsapp_integration'},
            {'name': 'mail.channel.view.form.inherit.all.in.one.whatsapp.integration', 'module': 'all_in_one_whatsapp_integration'},
            {'name': 'Odoo Studio: project.task.form customization', 'module': 'studio_customization'},
        ]

        # Build the query to join with ir_model_data
        conditions = []
        params = []
        if activate:
            for view in views_to_activate:
                conditions.append("(imd.module = %s AND regexp_replace(ir_ui_view.name, '\s+', '', 'g') LIKE %s)")
                params.extend([view['module'], view['name']])
        else:
            for view in views_to_archive:
                conditions.append("(imd.module = %s AND regexp_replace(ir_ui_view.name, '\s+', '', 'g') LIKE %s)")
                params.extend([view['module'], view['name']])

        if conditions:
            query = f"""
                UPDATE ir_ui_view 
                SET active = {activate} 
                FROM ir_model_data imd
                WHERE ir_ui_view.id = imd.res_id 
                AND imd.model = 'ir.ui.view'
                AND ({' OR '.join(conditions)})
            """
            self.env.cr.execute(query, tuple(params))

        #TODO: TO Fix issue in opening studio through sale

        self.env.cr.execute(f"""
                UPDATE ir_ui_view 
                SET active = False 
                FROM ir_model_data imd
                WHERE ir_ui_view.id = imd.res_id 
                AND imd.model = 'ir.ui.view'
                AND imd.name = 'odoo_studio_sale_ord_c4a0e911-98e8-4513-9c82-c6a90983b6a4'""")


    def update_views(self):
        """Activation and Deactivation of a list of views by their IDs"""
        self.update_using_name(activate = True)
        # view_ids_to_activate = [1422, 3063, 4558, 3062, 3512, 3513, 3431, 2807,
        #                         3777, 4193, 2801, 1688, 2851, 3776, 3247, 4255,
        #                         3996, 4033, 2806, 3243, 3665, 3493, 3787, 4813,
        #                         4215, 3419, 3685, 3058, 3258, 2803, 3863, 3535,
        #                         3360, 4014, 4144, 4337, 4364, 4495, 3666,
        #                         3536, 2800, 3829, 3739, 4513, 3497, 3705,
        #                         3674, 3758, 3842, 3759, 3839, 3914, 3825, 3848,
        #                         4363, 4022, 3393, 3819, 3864, 3726, 3552, 3495,
        #                         2850, 3472, 2811, 3351, 4452, 3245, 4483, 3249,
        #                         4358, 3899, 3397, 3394, 3524, 573 ]
        # query_1 = "UPDATE ir_ui_view SET active = TRUE WHERE id = ANY(%s)"
        # self.env.cr.execute(query_1, (view_ids_to_activate,))
        self.update_using_name()
        view_ids_to_archive = [3608, 3609, 3610, 8158, 8159, 4070,
                               3363, 3241, 3834,
                               4179, 4181, 4180, 4177, # these records are not in odoo 18 database . check it if issue occurs (issue maybe while db migration).
                               4178, 5769, # view is activated in the test server
                               3866,  #cannot see the view in alitkan_test
                               8070,  #cannot see the view in latest
                               3841,
                               4512, 4063, 8034, 8035]
        query_2 = "UPDATE ir_ui_view SET active = FALSE WHERE id = ANY(%s)"
        self.env.cr.execute(query_2, (view_ids_to_archive,))

        #TODO Remove unwanted fleet stages
        records = self.env['fleet.vehicle.state']

        for xml_id in [
            'fleet.fleet_vehicle_state_new_request',
            'fleet.fleet_vehicle_state_to_order',
            'fleet.fleet_vehicle_state_registered',
            'fleet.fleet_vehicle_state_downgraded',
        ]:
            rec = self.env.ref(xml_id, raise_if_not_found=False)
            if rec:
                records |= rec

        if records.exists():
            records.unlink()

        # query_3 = """update ir_model_data
        #             set model = 'discuss.channel'
        #             WHERE module = 'custom_pledges' AND name = 'deadline_notifications_channel';
        #             update ir_model_fields set name = 'custom_country_of_origin' where name ilike 'country_of_origin';
        #
        #             alter table product_template rename column country_of_origin to custom_country_of_origin;
        #
        #             UPDATE ir_ui_view
        #             SET active = FALSE
        #             WHERE arch_db::text LIKE '%property_supplier_payment_term_id%';
        #
        #             UPDATE ir_ui_view
        #             SET active = FALSE
        #             WHERE arch_db::text LIKE '%duplicate_bank_partner_ids%';
        #             delete from mail_group where alias_id = 1879;
        #
        #             DELETE FROM ir_asset
        #             WHERE path IN (
        #                 '/custom_sales/static/src/scss/custom_list_view.scss',
        #                 '/logistics/static/src/js/script.js',
        #                 '/custom_helpdesk/static/src/js/date_picker.js',
        #                 '/custom_helpdesk/static/src/js/filter_menu.js',
        #                 '/web_domain_field/static/lib/js/pyeval.js',
        #                 '/custom_contract/static/src/js/filter_menu.js',
        #                 '/custom_training/static/src/js/filter_menu.js',
        #                 '/custom_tac_ks/static/src/js/filter_menu.js',
        #                 '/custom_equipment/static/src/js/filter_menu.js',
        #                 '/confirm_on_status_change/static/src/js/relational_fields.js',
        #                 '/report_xlsx/static/src/js/report/action_manager_report.js',
        #                 '/custom_document/static/src/js/document_kanaban_controller.js',
        #                 '/account_move/static/src/js/reconcilation_model.js',
        #                 '/odoo_user_login_security/static/src/js/dashboard.js',
        #                 '/odoo_user_login_security/static/src/js/jquery.mousewheel.min.js',
        #                 '/odoo_user_login_security/static/src/js/login_activity.js'
        #                 '/odoo_user_login_security/static/src/js/owl.carousel.min.js',
        #                 '/odoo_user_login_security/static/src/js/update_que_ans.js',
        #                 '/odoo_user_login_security/static/src/css/dashboard.css',
        #                 '/odoo_user_login_security/static/src/css/owl.theme.default.min.css',
        #                 '/odoo_user_login_security/static/src/css/owl.carousel.min.css'
        #             )
        #             OR name = 'custom_contract.assets_backend_contract--view_id:3870--1';
        #             """
        # self.env.cr.execute(query_3)
        return True
