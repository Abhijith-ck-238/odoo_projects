/** @odoo-module **/
console.log('CylloActivityRenderer')
import { ActivityRenderer } from "@mail/views/web/activity/activity_renderer";
import { CylloActivityRecord } from "./cyllo_activity_record";
import { Component, onMounted, useState, onWillUnmount } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";
import { ActivityPopover } from "@cyllo_studio/js/views/cyllo_activity/cyllo_activity_popover_dailog";
import { getFormattedRecord, getImageSrcFromRecordInfo, isHtmlEmpty } from "@web/views/kanban/kanban_record";
//import { ActivityDialog } from "@cyllo_studio/js/views/cyllo_activity/cyllo_activity_dailog";
//import { DisplayNotification } from "@cyllo_studio/js/utils/display_notification";


export class CylloActivityRenderer extends ActivityRenderer {
	setup() {
		console.log("asdfgh", this)
		super.setup();
		this.rpc = useService('rpc');
		this.action = useService("action");

		onMounted(() => {
			console.log("sfygfdhhwihsjs", this)
			this.env.bus.trigger("ACTIVITY_DETAILS", {
				archInfo: this.props.archInfo,
				model: this.props.resModel,
				viewId: this.env.config.viewId,
				viewType: this.env.config.viewType,
				type:'dialog_box',
				fields: this.props.fields,
				activityResIds: this.props.activityResIds,
				records: this.props.records,
			});
		});
	}
	showEditButton(ev) {
		const editButton = document.querySelector('.cy-viewEdits').parentElement
		const editHighlight = editButton.querySelector('div')

		if (editButton && !editHighlight) {
			editButton.classList.add('edit-highlight')
			const messageDiv = document.createElement('div')
			messageDiv.className = 'cy-activity-edit-message';
			const spanElement = document.createElement('span');
			spanElement.textContent = 'Customise Activity Record';
			messageDiv.append(spanElement);
			editButton.append(messageDiv);

			setTimeout(() => {
				editButton.classList.remove('edit-highlight');
				if (editButton.contains(messageDiv)) {
					editButton.removeChild(messageDiv);
				}
			}, 3000);
		}
	}
}
CylloActivityRenderer.components = {
	...ActivityRenderer.components,
	CylloActivityRecord,
//	ActivityDialog,
}
CylloActivityRenderer.template = "cyllo_studio.CylloActivityRenderer"