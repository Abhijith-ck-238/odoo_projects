{
    'name': 'Custom HelpDesk',
    'category': 'Operations/Helpdesk',
    'version': '18.0.0.1',
    'summary': 'Helpdesk Customizations',
    'description': """
           1. Added overview to reports menu and added a new overview enu to show the tickets view.
           2. Change resource category 'Human' to 'People'.
           3. Updated domain for users (to show only Technical Users) on helpdesk.ticket when resource category is
            'Technician'.
           4. Added call_received_by field on helpdesk.ticket.
    """,
    'website': '',
    'depends': ['itkan_pm', 'mail'],
    'data': [
        'data/sequence_helpdesk_job_no.xml',
        'data/helpdesk_activity.xml',
        'data/action_compute_pm_date_in_month.xml',
        'data/action_set_resource_details.xml',
        'security/helpdesk_security.xml',
        'security/ir.model.access.csv',
        # 'views/filter_menu.xml',
        'views/ir_attachment_view.xml',
        'views/helpdesk_ticket.xml',
        'views/project_task_type_view.xml',
        'views/helpdesk_ticket_type_view.xml',
        'views/project_task_view.xml',
        'views/preventive_maintenanace_search.xml',
        'views/preventive_maintenance_view.xml',
        'views/helpdesk_res_settings_view.xml',
        'views/reservation_reason.xml',
        'views/agenda_view.xml',
        'views/helpdesk_stage_view.xml',
        'views/contract_modality.xml',
        'wizard/export_field_service_task_view.xml',
        'wizard/project_task_agenda.xml',
        # 'report/field_service_report.xml',
    ],
    # 'assets': {
    #     'web.assets_backend':[
    #         'custom_helpdesk/static/src/js/filter_menu.js',
    #         '/custom_helpdesk/static/src/js/date_picker.js',
    #         '/custom_helpdesk/static/src/xml/filter_menu.xml',
    #     ]
    # },
    # 'qweb': [
    #     "static/src/xml/filter_menu.xml",
    # ],
    'assets': {
        'web.assets_backend': [
            # 'custom_helpdesk/static/src/js/custom_html_widget.js',
            # 'custom_helpdesk/static/src/xml/custom_html_widget.xml',
            'custom_helpdesk/static/src/js/action_manager.js'
        ]
    },
    'installable': True,
    'application': False,
    'license': 'LGPL-3',
}
