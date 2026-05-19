odoo.define('custom_helpdesk.filter_menu', function (require){
"use strict";

var config = require('web.config');
var core = require('web.core');
var Domain = require('web.Domain');
var DropdownMenu = require('web.DropdownMenu');
var search_filters = require('web.search_filters');
var FilterMenu = require('web.FilterMenu');
var rpc = require('web.rpc');

var _t = core._t;
var QWeb = core.qweb;

FilterMenu.include({
    events: _.extend({}, DropdownMenu.prototype.events, {
        'click .o_add_custom_filter': '_onAddCustomFilterClick',
        'click .o_add_condition': '_onAddCondition',
        'click .o_pm_schedule_filter': '_onClickSchedule',
        'click .o_pm_schedule_apply': '_pmScheduleApply',
        'click .o_apply_filter': '_onApplyClick',
    }),

    _renderGeneratorMenu: function () {
        this.$el.find('.o_generator_menu').remove();
        this.$el.find('.o_pm_schedule_menu').remove();
        if (!this.generatorMenuIsOpen) {
            _.invoke(this.propositions, 'destroy');
            this.propositions = [];
        }
        if (this.__parentedParent.action.res_model == 'preventive.maintainence'){
            var $pmScheduleMenu = QWeb.render('PmScheduleMenu', {widget: this});
            this.$menu.append($pmScheduleMenu);
        }
        var $generatorMenu = QWeb.render('FilterMenuGenerator', {widget: this});
        this.$menu.append($generatorMenu);
        this.$addFilterMenu = this.$menu.find('.o_add_filter_menu');
        if (this.generatorMenuIsOpen && !this.propositions.length) {
            this._appendProposition();
        }
        this.$dropdownReference.dropdown('update');
    },

    _pmScheduleCommit: function(){
        var self = this
        var from_date = this.$el.find("#from_date").val();
        var to_date = this.$el.find("#to_date").val()
        var FromDate = this.dateConvertor(from_date)
        var toDate = this.dateConvertor(to_date)
        return rpc.query({
            model: 'preventive.maintainence',
            method: 'get_filter_records',
            args: [,FromDate, toDate]
        }).then(function (res) {
            var filters = _.invoke(self.propositions, 'get_filter').map(function () {
            return {
                type: "filter",
                description: `PM Schedule: ${FromDate} to ${toDate}`,
                domain: new Domain([['id', 'in', res]]).toString(),
            };
        });
        self.$el.find('#collapseOne').removeClass("show")
        self.$el.find('#collapseOne').css("display", "none");
        self.trigger_up('new_filters', {filters: filters});
        _.invoke(self.propositions, 'destroy');
        self.propositions = [];
        self._toggleCustomFilterMenu();
        });
    },

    dateConvertor(date){
       let dateObj = new Date(date);
       let dd = String(dateObj.getDate()).padStart(2, '0');
       let mm = String(dateObj.getMonth()+ 1).padStart(2, '0'); //January is 0!
       let yyyy = dateObj.getFullYear();
       return yyyy + '-' + mm + '-' + dd
    },

    _onClickSchedule: function(ev){
        ev.stopPropagation();
        if (this.$el.find('#collapseOne').hasClass("show")){
            this.$el.find('#collapseOne').removeClass("show")
            this.$el.find('#collapseOne').css("display", "none");
        }
        else{
            this.$el.find('#collapseOne').addClass("show")
            this.$el.find('#collapseOne').css("display", "block");
        }
    },

    _pmScheduleApply: function(ev){
        ev.stopPropagation();
        this._pmScheduleCommit();
        this._pmScheduleCommit();
    },
});

})