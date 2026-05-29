/** @odoo-module */
import {
    PivotModel
} from "@web/views/pivot/pivot_model";
import {
    patch
} from "@web/core/utils/patch";
import {
    computeReportMeasures,
    processMeasure
} from "@web/views/utils";

patch(PivotModel.prototype, {
    /**
     * @override
     */
    async load(searchParams) {
        this.searchParams = searchParams;
        const processedMeasures = processMeasure(searchParams.context.pivot_measures);
        const activeMeasures = processedMeasures || this.metaData.activeMeasures;
        const metaData = this._buildMetaData({
            activeMeasures
        });
        metaData.loadedActiveMeasures = [...processedMeasures || []]
        if (!this.reload) {
            metaData.rowGroupBys = [...searchParams.context.pivot_row_groupby || [], ...searchParams.groupBy, ...metaData.rowGroupBys]
            metaData.loadedRowGroupBy = [...searchParams.context.pivot_row_groupby || [], ...searchParams.groupBy]
            metaData.activeMeasures = [...new Set([
                ...(metaData.activeMeasures || []),
                ...(this.metaData.activeMeasures || [])
            ])];


            this.reload = true;
        } else {
            metaData.rowGroupBys = [...searchParams.groupBy, ...searchParams.context.pivot_row_groupby || [], ...metaData.rowGroupBys]
            metaData.loadedRowGroupBy = [...searchParams.groupBy, ...searchParams.context.pivot_row_groupby || []]
            metaData.activeMeasures = [...new Set([
                ...(metaData.activeMeasures || []),
                ...(this.metaData.activeMeasures || [])
            ])];

        }
        metaData.colGroupBys =
            searchParams.context.pivot_column_groupby || this.metaData.colGroupBys;

        if (JSON.stringify(metaData.rowGroupBys) !== JSON.stringify(this.metaData.rowGroupBys)) {
            metaData.expandedRowGroupBys = [];
        }
        if (JSON.stringify(metaData.colGroupBys) !== JSON.stringify(this.metaData.colGroupBys)) {
            metaData.expandedColGroupBys = [];
        }

        const allActivesMeasures = new Set(this.metaData.activeMeasures);
        if (processedMeasures) {
            processedMeasures.forEach((e) => allActivesMeasures.add(e));
        }

        metaData.measures = computeReportMeasures(metaData.fields, metaData.fieldAttrs, [
            ...allActivesMeasures,
        ]);
        const config = {
            metaData,
            data: this.data
        };
        return this._loadData(config);
    }
})