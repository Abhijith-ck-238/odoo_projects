odoo.define('custom_helpdesk.datepicker', function (require){
"use strict";

var core = require('web.core');
var field_utils = require('web.field_utils');
var time = require('web.time');
var Widget = require('web.Widget');
var web_datepicker = require('web.datepicker');

var _t = core._t;

web_datepicker.DateWidget.include({
    destroy: function () {
        if (this._onScroll) {
            window.removeEventListener('wheel', this._onScroll, true);
        }
        this.__libInput++;
        this.$el.datetimepicker('destroy');
        this.__libInput--;
        this._super.apply(this, arguments);
    },
    _onDateTimePickerHide: function () {
        this.__isOpen = false;
        this.changeDatetime();
        if (this._onScroll) {
            window.removeEventListener('wheel', this._onScroll, true);
        }
        this.changeDatetime();
    },
    _onDateTimePickerShow: function () {
        this.__isOpen = true;
        if (this.$input.val().length !== 0 && this.isValid()) {
            this.$input.select();
        }
        var self = this;
        this._onScroll = function (ev) {
            if (ev.target !== self.$input.get(0)) {
                self.__libInput++;
                self.$el.datetimepicker('hide');
                self.__libInput--;
            }
        };
        window.addEventListener('wheel', this._onScroll, true);
    },
})
web_datepicker.DateTimeWidget.in_onDateTimePickerShowclude({
    destroy: function () {
        if (this._onScroll) {
            window.removeEventListener('wheel', this._onScroll, true);
        }
        this.__libInput++;
        this.$el.datetimepicker('destroy');
        this.__libInput--;
        this._super.apply(this, arguments);
    },
    _onDateTimePickerHide: function () {
        this.__isOpen = false;
        this.changeDatetime();
        if (this._onScroll) {
            window.removeEventListener('wheel', this._onScroll, true);
        }
        this.changeDatetime();
    },
    _onDateTimePickerShow: function () {
        this.__isOpen = true;
        if (this.$input.val().length !== 0 && this.isValid()) {
            this.$input.select();
        }
        var self = this;
        this._onScroll = function (ev) {
            if (ev.target !== self.$input.get(0)) {
                self.__libInput++;
                self.$el.datetimepicker('hide');
                self.__libInput--;
            }
        };
        window.addEventListener('wheel', this._onScroll, true);
    },
})
})