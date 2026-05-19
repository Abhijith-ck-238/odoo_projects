/** @odoo-module **/
import {ExpressionEditorDialog} from "@web/core/expression_editor_dialog/expression_editor_dialog";

export class CylloExpressionEditorDialog extends ExpressionEditorDialog {
    static props = {
        ...ExpressionEditorDialog.props,
        setValidation: {type: Function, optional: true, default: () => {}}
    }
    onDiscard(){
        this.props.setValidation()
        this.props.close();
    }
}