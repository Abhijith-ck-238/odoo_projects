from odoo import models, api, fields
from datetime import date


class AccountMove(models.Model):
    _inherit = 'account.move'

    # @api.constrains(lambda self: ('name', 'date'))
    # def _constrains_date_sequence(self):
    #     """Override to bypass sequence validation for General Vendors Bills expense entries"""
    #     # Check if this is an expense sheet move for General Vendors Bills
    #     if self.expense_sheet_id and self.journal_id and 'General Vendors Bills' in self.journal_id.name:
    #         # Skip the sequence validation for these specific cases
    #         return
    #
    #     # Call the parent method for all other cases
    #     return super()._constrains_date_sequence()

    @api.model_create_multi
    def create(self, vals_list):
        """Override to force correct sequence for General Vendors Bills during creation"""
        # Check if any of the moves being created are expense sheet moves for General Vendors Bills
        for vals in vals_list:
            if (vals.get('expense_sheet_id') and 
                vals.get('journal_id')):
                
                journal = self.env['account.journal'].browse(vals['journal_id'])
                if journal and 'General Vendors Bills' in journal.name:
                    # Generate correct sequence for current year
                    current_year = fields.Date.context_today(self).year
                    
                    # Find the highest sequence number for current year in this journal
                    self.env.cr.execute("""
                        SELECT name FROM account_move 
                        WHERE journal_id = %s 
                        AND name LIKE %s 
                        AND name != '/'
                        ORDER BY name DESC 
                        LIMIT 1
                    """, (vals['journal_id'], f'VEB/{current_year}/%'))
                    
                    result = self.env.cr.fetchone()
                    if result and result[0]:
                        # Extract sequence number and increment
                        last_seq = int(result[0].split('/')[-1])
                        new_seq = last_seq + 1
                    else:
                        # Start with 0001 for current year
                        new_seq = 1
                    
                    # Force the correct sequence
                    vals['name'] = f"VEB/{current_year}/{new_seq:04d}"
        
        return super().create(vals_list)
    
    def _get_correct_sequence_for_current_year(self):
        """Generate correct sequence for current year"""
        current_year = fields.Date.context_today(self).year
        
        # Find the highest sequence number for current year in this journal
        self.env.cr.execute("""
            SELECT name FROM account_move 
            WHERE journal_id = %s 
            AND name LIKE %s 
            AND name != '/'
            ORDER BY name DESC 
            LIMIT 1
        """, (self.journal_id.id, f'VEB/{current_year}/%'))
        
        result = self.env.cr.fetchone()
        if result and result[0]:
            # Extract sequence number and increment
            last_seq = int(result[0].split('/')[-1])
            new_seq = last_seq + 1
        else:
            # Start with 0001 for current year
            new_seq = 1
        
        return f"VEB/{current_year}/{new_seq:04d}"
