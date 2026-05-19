from odoo import models, api


class CustomProductTemplate(models.Model):
    _inherit = 'product.template'

    @api.model
    def fields_get(self, allfields=None, attributes=None):
        fields_to_hide = ['standard_price']
        res = super(CustomProductTemplate, self).fields_get()
        for field in fields_to_hide:
            if self.env.user.has_group('sales_team.group_sale_salesman') or self.env.user.has_group(
                    'access_units.sale_confirm_sale_order') or self.env.user.has_group(
                'access_units.sale_ignore_access_units') or self.env.user.has_group(
                'custom_sales.report_access_limited_users') or self.env.user.has_group(
                'sales_team.group_sale_salesman_all_leads') or self.env.user.has_group(
                'sales_team.group_sale_manager') or self.env.user.has_group('stock.group_stock_user'):
                res[field]['exportable'] = False
        return res


class CustomProductProduct(models.Model):
    _inherit = 'product.product'

    @api.model
    def fields_get(self, allfields=None, attributes=None):
        fields_to_hide = ['standard_price']
        res = super(CustomProductProduct, self).fields_get()
        for field in fields_to_hide:
            if self.env.user.has_group('sales_team.group_sale_salesman') or self.env.user.has_group(
                    'access_units.sale_confirm_sale_order') or self.env.user.has_group(
                'access_units.sale_ignore_access_units') or self.env.user.has_group(
                'custom_sales.report_access_limited_users') or self.env.user.has_group(
                'sales_team.group_sale_salesman_all_leads') or self.env.user.has_group(
                'sales_team.group_sale_manager') or self.env.user.has_group('stock.group_stock_user'):
                res[field]['exportable'] = False
        return res
