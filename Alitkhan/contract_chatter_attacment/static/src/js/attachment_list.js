import {onWillStart} from "@odoo/owl";
import {useService} from "@web/core/utils/hooks";
import {patch} from "@web/core/utils/patch";

import {AttachmentList} from "@mail/core/common/attachment_list";


patch(AttachmentList.prototype, {
    setup() {
        super.setup();
        this.orm = useService('orm');
        this.invisible_attachment = []
        onWillStart(async () => {
            if (this.env.inChatter?.thread.model === "contract.contract") {
                const invisible_attachment = await this.orm.call(
                    'contract.contract',
                    'get_invisible_attachment_ids',
                    [[this.env.inChatter.thread.id]]
                );
                this.invisible_attachment = invisible_attachment
            }

        });
    },
    get images() {
        return this.props.attachments.filter((a) => a.isImage).filter((a) => !this.invisible_attachment.includes(a.id));
    },
    get cards() {
        return this.props.attachments.filter((a) => !a.isImage).filter((a) => !this.invisible_attachment.includes(a.id));
    }
});
