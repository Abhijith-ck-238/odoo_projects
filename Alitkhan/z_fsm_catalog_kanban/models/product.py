from odoo.addons.industry_fsm_stock.models.product import ProductProduct

from odoo import _
from odoo.exceptions import UserError



def patch_write(self, vals):
    if 'fsm_quantity' in vals:
        for product in self:
            # Find all sale order lines using this product
            task_id = self.env['project.task'].browse(self.env.context.get('fsm_task_id'))
            if (task_id.sale_order_id.state == 'sale' and product.fsm_quantity - vals['fsm_quantity'] > product.quantity_decreasable_sum):
                raise UserError(_('The ordered quantity cannot be decreased below the amount already delivered. Instead, create a return in your inventory.'))
    return super(ProductProduct,self).write(vals)

# Apply patch ONLY to enterprise-18.0/industry_fsm_stock --> class ProductProduct
ProductProduct.write = patch_write