from odoo import fields, models


class TechnicalProduct(models.Model):
    _name = 'technical.product'
    _description = 'Technical Product'

    name = fields.Char('Product Name', translate=True)
    partner_id = fields.Many2one('res.partner', 'Supplier')
    modality = fields.Many2one('contract.modality', 'Modality')
    default_code = fields.Char('Internal Reference')
    active = fields.Boolean(default=True)
    is_technical_product = fields.Boolean(default=True)

    def map_technical_products(self):
        self.env.cr.execute("""
        INSERT INTO technical_product (id, name, default_code, partner_id, modality, active, is_technical_product )
         SELECT product_product.id,
            product_template.name,
            product_product.default_code,
             product_template.partner_id,
              product_template.modality, 
              product_product.active,
            product_template.is_technical_product 
            FROM product_product 
            join product_template on product_template.id = product_product.product_tmpl_id
             where product_template.is_technical_product = True and product_product.id NOT IN (SELECT id FROM technical_product)
             """)

    def map_contract_products(self):
        print("map")
        self.env.cr.execute("""
            INSERT INTO technical_product (id, name, default_code, partner_id, modality, active, is_technical_product)
            SELECT DISTINCT
                product_product.id,
                product_template.name,
                product_product.default_code,
                product_template.partner_id,
                product_template.modality,
                product_product.active,
                product_template.is_technical_product
            FROM product_product
            JOIN product_template ON product_template.id = product_product.product_tmpl_id
            JOIN contract_product ON product_product.id = contract_product.technical_product
            ON CONFLICT (id) DO NOTHING
        """)
    