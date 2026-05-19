/** @odoo-module **/
import { patch } from "@web/core/utils/patch";
import { useService } from "@web/core/utils/hooks";
import { Chatter } from "@mail/core/web/chatter";
import {ChatterDialog} from'./chatter_dialog';
import {  onMounted } from "@odoo/owl";
import {_t} from "@web/core/l10n/translation";

Chatter.props = [...Chatter.props, 'cyXpath?']

patch(Chatter.prototype, {
  setup() {
    super.setup();
        this.dialogService = useService("dialog")
            this.notification = useService('effect')
      onMounted(() => {
        const preview = document.querySelector('o_attachment_preview')
      })
    },
    async onClick(ev,position) {
        const preview = document.querySelector('.chatter-preview')
        if(!preview){
          this.dialogService.add(ChatterDialog, {
            title: 'Remove Chatter',
            model: this.env.model.config.resModel,
            view_id: this.env.config.viewId,
            path:this.props.cyXpath,
            position: position,
        });
        }else{
           this.notification.add({
                    title: _t("Unable To Remove Chatter"),
                    message: "You Cannot Remove Chatter In This Model.",
                    type: "notification_panel",
                    notificationType: "warning",
            });
        }

    }

});

Chatter.components = {
   ...Chatter.components,

}