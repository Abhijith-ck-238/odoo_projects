/** @odoo-module */
import { registry} from '@web/core/registry';
import { Layout } from "@web/search/layout";
import { useModel } from "@web/model/model";
import { SearchBar } from "@web/search/search_bar/search_bar";
import { useSearchBarToggler } from "@web/search/search_bar/search_bar_toggler";
import { CogMenu } from "@web/search/cog_menu/cog_menu";
import { useService } from "@web/core/utils/hooks";
import { useState } from "@odoo/owl";
import { jsonrpc } from "@web/core/network/rpc_service";
const { Component, mount} = owl
export class ReportView extends Component {
	setup(){
    	this.action = useService("action");
        this.rpc = useService("rpc");
        this.orm = useService("orm");
         this.state = useState({
            reportData: {},
            QwebCode:{},
        })
//         onWillStart(async ()=>{
//        if(!this.env.config.viewId){
//                await this.rpc('cyllo_studio/search/add/search_view',{
//                    arch: serializeXML(this.props.arch),
//                    model: this.props.resModel,
//                })
//                await this.action.doAction('studio_reload')
//            }
//        })
    	this.loadData();
	}
	async loadData(){
    	this.state.reportData = await jsonrpc('/web/dataset/call_kw/ir.actions.report/get_values', {
                model: 'ir.actions.report',
                method: 'get_values',
                args: [[]],
                kwargs: {},
            });
            console.log(this.state.reportData)
	}

	async ReportOnClick(ev, data){
	console.log("jvj", data)
        this.state.QwebCode = await this.orm.call("ir.actions.report", "get_qweb", [data], {});
        console.log("corresponding report",this.state.QwebCode)
        const reportUrl = `/my_module/report/${data.id}`;
        window.open(reportUrl, "_blank");



//	   this.action.doAction({
//            type: "ir.actions.client",
//            tag: "report_view",
//        });
	}
//	onClickReport
}
ReportView.template = "report_view.report_view"
registry.category("actions").add("report_view", ReportView)
ReportView.components = {
    Layout,
    CogMenu,
    SearchBar
}