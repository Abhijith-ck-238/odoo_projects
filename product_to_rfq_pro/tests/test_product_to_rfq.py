# -*- coding: utf-8 -*-
from odoo.tests import TransactionCase, tagged
from odoo import fields


@tagged('post_install', '-at_install')
class TestProductToRfq(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super(TestProductToRfq, cls).setUpClass()
        
        # Create a vendor
        cls.partner = cls.env['res.partner'].create({
            'name': 'Test Vendor',
        })
        
        # Create a product
        cls.product = cls.env['product.product'].create({
            'name': 'Test Product',
            'type': 'consu',
            'list_price': 100.0,
            'standard_price': 50.0,
        })
        
        # Create a purchase order
        cls.purchase_order = cls.env['purchase.order'].create({
            'partner_id': cls.partner.id,
        })

    def test_action_view_products(self):
        """Test action_view_products in purchase order."""
        action = self.purchase_order.action_view_products()
        self.assertEqual(action.get('res_model'), 'product.product')
        self.assertEqual(action.get('type'), 'ir.actions.act_window')
        self.assertTrue(action.get('context', {}).get('purchase_button'))

    def test_product_to_rfq_wizard(self):
        """Test adding product to RFQ using the wizard."""
        # Create the wizard
        wizard = self.env['product.to.rfq'].create({
            'product_id': self.product.id,
            'order_id': self.purchase_order.id,
            'qty': 5.0,
            'price_unit': 45.0,
        })
        
        # Add to RFQ
        action = wizard.action_add_to_rfq()
        self.assertEqual(action.get('type'), 'ir.actions.client')
        self.assertEqual(action.get('tag'), 'display_notification')
        
        # Check if the order line is created
        order_line = self.purchase_order.order_line.filtered(lambda l: l.product_id == self.product)
        self.assertTrue(order_line, "Order line should be created")
        self.assertEqual(order_line.product_qty, 5.0)
        self.assertEqual(order_line.price_unit, 45.0)
        
        # Add the same product with the same price again
        wizard_2 = self.env['product.to.rfq'].create({
            'product_id': self.product.id,
            'order_id': self.purchase_order.id,
            'qty': 3.0,
            'price_unit': 45.0,
        })
        wizard_2.action_add_to_rfq()
        
        # Quantity should be updated (5 + 3 = 8)
        self.assertEqual(order_line.product_qty, 8.0)
        self.assertEqual(len(self.purchase_order.order_line), 1, "Should not create a new line if product and price are same")

        # Add the same product with a different price
        wizard_3 = self.env['product.to.rfq'].create({
            'product_id': self.product.id,
            'order_id': self.purchase_order.id,
            'qty': 2.0,
            'price_unit': 50.0,
        })
        wizard_3.action_add_to_rfq()
        
        # Should create a new line
        self.assertEqual(len(self.purchase_order.order_line), 2, "Should create a new line for different price")
        new_order_line = self.purchase_order.order_line.filtered(lambda l: l.price_unit == 50.0)
        self.assertEqual(new_order_line.product_qty, 2.0)

    def test_onchange_recent_date(self):
        """Test the population of recent purchases."""
        # First, confirm the purchase order to make it 'purchase' state
        self.purchase_order.order_line = [(0, 0, {
            'product_id': self.product.id,
            'product_qty': 10,
            'price_unit': 40.0,
            'date_planned': fields.Datetime.now(),
        })]
        self.purchase_order.button_confirm()
        
        # Create wizard as new record for onchange testing
        wizard = self.env['product.to.rfq'].new({
            'product_id': self.product.id,
            'order_id': self.purchase_order.id,
        })
        
        # Trigger onchange
        wizard._onchange_recent_date()
        
        # It should have found the recent purchase line
        self.assertTrue(wizard.recent_products_ids, "Should populate recent products")
        self.assertEqual(wizard.recent_products_ids[0].order_line_id, self.purchase_order.order_line[0])
