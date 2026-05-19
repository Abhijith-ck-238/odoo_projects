/** @odoo-module */
import { FSMProductCatalogKanbanRecord } from "@industry_fsm_sale/components/product_catalog/kanban_record";
import { patch } from "@web/core/utils/patch";


patch(FSMProductCatalogKanbanRecord.prototype, {
	async updateQuantity(quantity) {
		const orderId = this.props.record.context.order_id;
		let saleState = null;
		if (orderId) {
			const result = await this.orm.read("sale.order", [orderId], ["state"]);
			saleState = result?.[0]?.state;
		}
		if (saleState !== "sale" && saleState !== "done") {
			if (quantity < this.productCatalogData.minimumQuantityOnProduct) {
				this.customUpdateQuantity(Math.min(quantity, this.productCatalogData.minimumQuantityOnProduct));

			} else {
				this.customUpdateQuantity(quantity);
			}
		} else {

			if (this.productCatalogData.tracking) {
				this.customUpdateQuantity(this.productCatalogData.quantity);
			} else {
				if (
					this.productCatalogData.quantity === this.productCatalogData.minimumQuantityOnProduct &&
					quantity < this.productCatalogData.quantity
				) {

					// This condition is only triggered when the product was already at the minimum quantity
					// possible, as stated in the fsm_stock module, then the user inputs a quantity lower
					// than this limit, in this case we need the record to forcefully update the record.
					this.props.record.load();
					this.props.record.model.notify();
				} else {
					this.customUpdateQuantity(Math.max(quantity, this.productCatalogData.minimumQuantityOnProduct));
				}
			}
		}
	},
});