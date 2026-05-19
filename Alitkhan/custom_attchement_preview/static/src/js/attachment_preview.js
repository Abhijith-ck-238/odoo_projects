import { registry } from "@web/core/registry";
import { BinaryField, binaryField } from "@web/views/fields/binary/binary_field";
import { download } from "@web/core/network/download";

export class AttachmentPreviewField extends BinaryField {
    static template = "custom_attachment_preview.AttachmentPreviewField";

    setup() {
    super.setup();
    this.onPreviewClick = this.onPreviewClick.bind(this);
    this.onFileDownload = this.onFileDownload.bind(this);
    this.onClearClick = this.onClearClick.bind(this);
}

onPreviewClick(ev) {
    ev.preventDefault();
    const val = this.props.record.data[this.props.name];
    if (!val) return;
    const fileUrl = `/web/content?model=${this.props.record.resModel}&id=${this.props.record.resId}&field=${this.props.name}&download=false`;
    window.open(fileUrl, "_blank");
}

async onFileDownload(ev) {
    ev.preventDefault();
    await download({
        data: {
            model: this.props.record.resModel,
            id: this.props.record.resId,
            field: this.props.name,
            filename_field: this.fileName,
            download: true,
        },
        url: "/web/content",
    });
}

onClearClick(ev) {
    ev.preventDefault();
    this.update({});
}

}

export const binary_attachment_preview = {
    ...binaryField,
    component: AttachmentPreviewField,
};

registry.category("fields").add("binary_attachment_preview", binary_attachment_preview);
