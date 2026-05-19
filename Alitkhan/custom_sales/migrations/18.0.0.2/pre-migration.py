from odoo import api, SUPERUSER_ID, Command


def migrate(cr, version):
    cr.execute("""
               DELETE FROM ir_asset
WHERE path LIKE '%list_view.scss%';
               """)
