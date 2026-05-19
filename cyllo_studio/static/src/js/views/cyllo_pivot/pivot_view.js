/** @odoo-module */
import {
    _t
} from "@web/core/l10n/translation";
import {
    registry
} from "@web/core/registry";
import {
    pivotView
} from "@web/views/pivot/pivot_view";
import {
    CylloPivotRenderer
} from './pivot_renderer'

export const CylloPivotView = {
    ...pivotView,
    Renderer: CylloPivotRenderer,
    props: (genericProps, view) => {
        const modelParams = {};
        if (genericProps.state && false) {
            modelParams.data = genericProps.state.data;
            modelParams.metaData = genericProps.state.metaData;
        } else {
            const {
                arch,
                fields,
                resModel
            } = genericProps;
            // parse arch
            const archInfo = new view.ArchParser().parse(arch);
            if (!archInfo.activeMeasures.length || archInfo.displayQuantity) {
                archInfo.activeMeasures.unshift("__count");
            }
            modelParams.metaData = {
                activeMeasures: archInfo.activeMeasures,
                colGroupBys: archInfo.colGroupBys,
                defaultOrder: archInfo.defaultOrder,
                disableLinking: Boolean(archInfo.disableLinking),
                displayQuantity: Boolean(archInfo.displayQuantity),
                sticky: Boolean(archInfo.sticky),
                fields: fields,
                fieldAttrs: archInfo.fieldAttrs,
                resModel: resModel,
                rowGroupBys: archInfo.rowGroupBys,
                title: archInfo.title || _t("Untitled"),
                widgets: archInfo.widgets,
                colPath: archInfo.colPath,
                rowPath: archInfo.rowPath,
                measurePath: archInfo.measurePath,
            };
        }

        return {
            ...genericProps,
            Model: view.Model,
            modelParams,
            Renderer: view.Renderer,
        };
    }
};

registry.category("views").add("pivot", CylloPivotView, {
    force: true
});