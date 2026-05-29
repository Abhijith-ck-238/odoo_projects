from . import models



def post_init_hook(env):
    """initially while installing this module, the noupdate will be set to false and while we try to upgrade corresponding modules,
           the data will be uploaded
    """
    # TODO: update noupdate to false
    env['ir.model.data'].search([('module', '=', 'stock'),('name','=','product_template_action_product')]).write({
        'noupdate': False
    })
    env['ir.model.data'].search([('module', '=', 'industry_fsm'),('name','=','planning_project_stage_0')]).write({
        'noupdate': False
    })
    env['ir.model.data'].search([('module', '=', 'industry_fsm'),('name','=','planning_project_stage_1')]).write({
        'noupdate': False
    })
    env['ir.model.data'].search(
        [('module', '=', 'custom_pledges'), ('name', '=', 'action_pledge_assets_kanban')]).write({'noupdate': False})
    env['ir.model.data'].search([
        ('module', '=', 'custom_helpdesk'),
        ('name', '=', 'helpdesk_agenda_action')
    ]).write({'noupdate': False})


    # TODO: Edit FSM STAGES
    """edit the field service stages order"""
    stage_1 = env.ref('industry_fsm.planning_project_stage_1').id
    env.ref('industry_fsm.planning_project_stage_2').action_archive()
    env.ref('industry_fsm.planning_project_stage_3').action_archive()
    env.ref('industry_fsm.planning_project_stage_4').action_archive()
    env.cr.execute(f'''
                    UPDATE project_task_type 
                    SET name = '{{"en_US": "Done"}}',
                        sequence = 7
                    WHERE id = {stage_1}
                ''')

    #TODO : ARCHIVE UNWANTED VIEWS
    employee_rule = (env.ref("custom_expense.ir_rule_hr_expense_sheet_employee", raise_if_not_found=False))
    if employee_rule and employee_rule.exists():
        employee_rule.action_archive()

    # TODO: REMOVE THE HELPDESK TAGS
    # Execute the SQL query to update descriptions
    env.cr.execute("""
                        UPDATE helpdesk_ticket
                        SET description = REGEXP_REPLACE(description, '<p>|</p>', '', 'g')
                        WHERE description IS NOT NULL
                        """)
    # Invalidate cache for the 'description' field
    field = env['helpdesk.ticket']._fields['description']
    env.cache.invalidate([(field, None)])

    # TODO: ARCHIVE THE MY BUDGET MENU IN HR EXPENSE
    env.ref("custom_expense.menu_hr_expense_my_budget").action_archive()

    #TODO: ACTIVATE AND INACTIVATE VIEWS
    """Activation and Deactivation of a list of views by their IDs"""
    view_ids_to_activate = [1422, 4558, 3513, 3431, 2807,
                            3777, 4193, 2801, 1688, 2851, 3776, 3247, 4255,
                            3996, 4033, 2806, 3243, 3493, 3787, 4813,
                            4215, 3419, 3058, 3258, 2803, 3863, 3535, 4358,
                            3360, 4014, 4512, 4144, 4337, 4364, 4495, 3666,
                            3536, 2800, 4063, 3829, 3739, 4513, 3497, 3705,
                            3674, 3758, 3842, 3759, 3839, 3914, 3848,
                            4363, 4022, 3393, 3819, 3864, 3726, 3552, 3495,
                            2850, 3472, 2811, 3351, 4452, 3245, 4483, 3249,
                             ]
    # query_1 = "UPDATE ir_ui_view SET active = TRUE WHERE id = ANY(%s)"
    # env.cr.execute(query_1, (view_ids_to_activate,))
    view_ids_to_archive = [3543, 3608, 3609, 3610, 8158, 8159, 4070,
                           3363, 3241, 3834, 4179, 4181, 4180, 4177,
                           4178, 5769, 4179, 4181, 4180, 3866, 8070,
                           2803, 3536, 3841, 8034, 8035, 3685, 3801,
                           3665, 4483, 3062, 3063, 3512, 3513]
    query_2 = "UPDATE ir_ui_view SET active = FALSE WHERE id = ANY(%s)"
    env.cr.execute(query_2, (view_ids_to_archive,))

    query_3 = """update ir_model_data 
                                set model = 'discuss.channel'
                                WHERE module = 'custom_pledges' AND name = 'deadline_notifications_channel';

                                UPDATE ir_ui_view
                                SET active = FALSE
                                WHERE arch_db::text LIKE '%property_supplier_payment_term_id%';

                                UPDATE ir_ui_view
                                SET active = FALSE
                                WHERE arch_db::text LIKE '%duplicate_bank_partner_ids%';
                                delete from mail_group where alias_id = 1879;

                                DELETE FROM ir_asset 
                                WHERE path IN (
                                    '/custom_sales/static/src/scss/custom_list_view.scss',
                                    '/logistics/static/src/js/script.js',
                                    '/custom_helpdesk/static/src/js/date_picker.js',
                                    '/custom_helpdesk/static/src/js/filter_menu.js',
                                    '/web_domain_field/static/lib/js/pyeval.js',
                                    '/custom_contract/static/src/js/filter_menu.js',
                                    '/custom_training/static/src/js/filter_menu.js',
                                    '/custom_tac_ks/static/src/js/filter_menu.js',
                                    '/custom_equipment/static/src/js/filter_menu.js',
                                    '/confirm_on_status_change/static/src/js/relational_fields.js',
                                    '/report_xlsx/static/src/js/report/action_manager_report.js',
                                    '/custom_document/static/src/js/document_kanaban_controller.js',
                                    '/account_move/static/src/js/reconcilation_model.js',
                                    '/odoo_user_login_security/static/src/js/dashboard.js',
                                    '/odoo_user_login_security/static/src/js/jquery.mousewheel.min.js',
                                    '/odoo_user_login_security/static/src/js/login_activity.js'
                                    '/odoo_user_login_security/static/src/js/owl.carousel.min.js',
                                    '/odoo_user_login_security/static/src/js/update_que_ans.js',
                                    '/odoo_user_login_security/static/src/css/dashboard.css',
                                    '/odoo_user_login_security/static/src/css/owl.theme.default.min.css',
                                    '/odoo_user_login_security/static/src/css/owl.carousel.min.css'
                                )   
                                OR name = 'custom_contract.assets_backend_contract--view_id:3870--1';
                                """
    env.cr.execute(query_3)

    # TODO: Fixing contract access issue
    """set the res_id to all the attachments inside the attachment's
             fields of contract and contract product models"""
    env.cr.execute('''
                        UPDATE ir_attachment
                        SET res_id    = rel.contract_id,
                            res_model = 'contract.contract' FROM attachement_contracts_docs_rel rel
                        WHERE ir_attachment.id = rel.attachment_id
                          AND (ir_attachment.res_id != rel.contract_id
                           OR ir_attachment.res_id IS NULL)
                   ''')
    env.cr.execute('''
                        UPDATE ir_attachment
                        SET res_id    = rel.contract_line_id,
                            res_model = 'contract.product' FROM attachment_contract_line_pac_document_rel rel
                        WHERE ir_attachment.id = rel.attachment_id
                          AND (ir_attachment.res_id != rel.contract_line_id
                           OR ir_attachment.res_id IS NULL)
                        ''')


    # agenda_gantt_view = env.ref(
    #     "custom_helpdesk.agenda_gantt_view",
    #     raise_if_not_found=False
    # )
    # if agenda_gantt_view and agenda_gantt_view.exists():
    #     agenda_gantt_view.action_archive()

    return True

