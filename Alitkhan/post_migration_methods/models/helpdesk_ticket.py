# -*- coding: utf-8 -*-
import xmlrpc.client
from odoo import models, fields


class HelpDeskTicket(models.Model):
    _inherit = "helpdesk.ticket"

    ticket_type_id = fields.Many2one('helpdesk.ticket.type', string="Ticket Type")
    # def action_remove_html_tag(self):
    #     records = self.env["helpdesk.ticket"].search([])
    #     for rec in records:
    #         if rec.description:
    #             cleaned_description = rec.description.replace('<p>', '').replace('</p>', '').strip()
    #             rec.write({
    #                 'description': cleaned_description
    #             })
    def action_remove_html_tag(self):
        # Execute the SQL query to update descriptions
        self.env.cr.execute("""
                UPDATE helpdesk_ticket
                SET description = REGEXP_REPLACE(description, '<p>|</p>', '', 'g')
                WHERE description IS NOT NULL
            """)
        # Invalidate cache for the 'description' field
        field = self.env['helpdesk.ticket']._fields['description']
        self.env.cache.invalidate([(field, None)])

    def fetchByQuery(self):
        """Fetch data through query"""
        self.env.cr.execute("""WITH tag_choices AS (
                                    SELECT
                                        ht.id AS ticket_id,
                                        htag.name->>'en_US' AS tag_name,
                                        COUNT(rel.helpdesk_tag_id) OVER (PARTITION BY ht.id) AS tag_count,
                                        ROW_NUMBER() OVER (PARTITION BY ht.id ORDER BY rel.helpdesk_tag_id) AS tag_order
                                    FROM helpdesk_ticket ht
                                    JOIN helpdesk_tag_helpdesk_ticket_rel rel ON ht.id = rel.helpdesk_ticket_id
                                    JOIN helpdesk_tag htag ON rel.helpdesk_tag_id = htag.id
                                ),
                                first_tag_match AS (
                                    SELECT ticket_id, tag_name, tag_order
                                    FROM tag_choices
                                    WHERE 
                                        -- Case 1: Only one tag → use it
                                        (tag_count = 1 AND tag_order = 1)
                                        
                                        -- Case 2: Multiple tags → ignore first, match allowed names
                                        OR (tag_count > 1 AND tag_order > 1 AND tag_name IN (
                                            'Regular Check', 'Defect', 'Training', 'Installation',
                                            'Preventive maintenance', 'Note', 'Application', 'Update'
                                        ))
                                ),
                                ranked_choices AS (
                                    SELECT ticket_id, tag_name,
                                        ROW_NUMBER() OVER (PARTITION BY ticket_id ORDER BY tag_order) AS rank_choice
                                    FROM first_tag_match
                                ),
                                final_tag AS (
                                    SELECT ticket_id, tag_name
                                    FROM ranked_choices
                                    WHERE rank_choice = 1
                                )
                                UPDATE helpdesk_ticket ht
                                SET ticket_type_id = htt.id
                                FROM final_tag ft
                                JOIN helpdesk_ticket_type htt ON htt.name->>'en_US' = ft.tag_name
                                WHERE ht.id = ft.ticket_id;
                                """)
        return {}


    def fetchTicketType(self):
        """Fetch ticket type and assign them in helpdesk tickets"""
        url_db1 = "http://191.101.164.149:8069" # THe server from the data is been fetched
        db_1 = 'LiveDB'
        username_db_1 = 'admin'
        password_db_1 = '552Tk4-d3!O$'
        common_1 = xmlrpc.client.ServerProxy('{}/xmlrpc/2/common'.format(url_db1),allow_none=True)
        models_1 = xmlrpc.client.ServerProxy('{}/xmlrpc/2/object'.format(url_db1),allow_none=True)
        version_db1 = common_1.version()

        url_db2 = "http://109.123.246.211:8069"
        # url_db2 = "http://10.0.21.2:8018"
        # db_2 = 'ALITKAN_1'
        # db_2 = 'Alitkan_Test'
        db_2 = 'Alitkan_18_live'
        username_db_2 = 'admin'
        password_db_2 = '552Tk4-d3!O$'
        common_2 = xmlrpc.client.ServerProxy('{}/xmlrpc/2/common'.format(url_db2),allow_none=True)
        models_2 = xmlrpc.client.ServerProxy('{}/xmlrpc/2/object'.format(url_db2),allow_none=True)
        version_db2 = common_2.version()

        uid_db1 = common_1.authenticate(db_1, username_db_1, password_db_1, {})
        uid_db2 = common_2.authenticate(db_2, username_db_2, password_db_2, {})
        count = 0
        new_partners = {}
        db_1_ticket_type = models_1.execute_kw(db_1, uid_db1, password_db_1, 'helpdesk.ticket.type',
                                               'search_read', [], {})
        [item.pop('__last_update', None) for item in db_1_ticket_type]

        db_2_ticket_type = models_2.execute_kw(db_2, uid_db2, password_db_2,
                                               'helpdesk.ticket.type', 'search_read', [], {})
        for rec in db_1_ticket_type:
            is_present = any(item.get('name') == rec.get('name') for item in db_2_ticket_type)
            if not is_present:
                migrated_partner = models_2.execute_kw(db_2, uid_db2, password_db_2,
                                                       'helpdesk.ticket.type', 'create', [{
                        'name': rec['name'],
                        'id': rec['id'],
                        'sequence': rec['sequence'],
                        'require_service_report': rec['require_service_report'],
                        'allowed_fs_stages': rec['allowed_fs_stages'],
                        'is_to_hide_other_stages': rec['is_to_hide_other_stages'],
                        'is_reported_by_required': rec['is_reported_by_required'],
                        'show_contract_status': rec['show_contract_status'],
                        'bad_use': rec['bad_use'],
                        'is_show_product_cart': rec['is_show_product_cart'],
                        'can_edit_task_range': rec['can_edit_task_range'],
                        'display_name': rec['display_name'],
                        'create_date': rec['create_date'],
                        'write_date': rec['write_date'],
                        'write_uid': rec['write_uid'][0] if rec[
                            'write_uid'] else False,
                        'create_uid': rec['create_uid'][0] if rec[
                            'create_uid'] else False,
                        'exception_id': rec['exception_id'][0] if rec[
                            'exception_id'] else False,
                        'subticket_exception_id': rec['subticket_exception_id'][0] if rec[
                            'subticket_exception_id'] else False,

                    }])



        db_2_ticket_type_by_query = models_2.execute_kw(db_2, uid_db2, password_db_2,
                                           'helpdesk.ticket', 'fetchByQuery', [[]], {})





        # count = 0
        # new_partners = {}
        # for rec in db_1_ticket_type:
        #     is_present = any(item.get('name') == rec.get('name') for item in db_2_ticket_type)
        #     if not is_present:
        #
        #         migrated_partner = models_2.execute_kw(db_2, uid_db2, password_db_2,
        #                                                'helpdesk.ticket.type', 'create', [{
        #                 'name': rec['name'],
        #                 'id': rec['id'],
        #                 'sequence': rec['sequence'],
        #                 'require_service_report': rec['require_service_report'],
        #                 'allowed_fs_stages': rec['allowed_fs_stages'],
        #                 'is_to_hide_other_stages': rec['is_to_hide_other_stages'],
        #                 'is_reported_by_required': rec['is_reported_by_required'],
        #                 'show_contract_status': rec['show_contract_status'],
        #                 'bad_use': rec['bad_use'],
        #                 'is_show_product_cart': rec['is_show_product_cart'],
        #                 'can_edit_task_range': rec['can_edit_task_range'],
        #                 'display_name': rec['display_name'],
        #                 'create_date': rec['create_date'],
        #                 'write_date': rec['write_date'],
        #                 'write_uid': rec['write_uid'][0] if rec[
        #                     'write_uid'] else False,
        #                 'create_uid': rec['create_uid'][0] if rec[
        #                     'create_uid'] else False,
        #                 'exception_id': rec['exception_id'][0] if rec[
        #                     'exception_id'] else False,
        #                 'subticket_exception_id': rec['subticket_exception_id'][0] if rec[
        #                     'subticket_exception_id'] else False,
        #
        #             }])


