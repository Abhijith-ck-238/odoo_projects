/** @odoo-module **/
import publicWidget from "@web/legacy/js/public/public_widget";
import { Dialog } from "@web/core/dialog/dialog";

import { useService } from "@web/core/utils/hooks";
publicWidget.registry.Location = publicWidget.Widget.extend({
    selector: '#whole_sub',
    events: {
        'click #location_id': '_onLocationClick',
        'click #dismiss': '_onCloseClick',
        'click #next': '_onNextClick'
    },
    init() {
        this._super(...arguments);
        this.orm = this.bindService("orm");
    },
    setup() {
        super.setup();
        //        this.location = useService("location");
    },
    _onLocationClick() {
        var location = this.el.querySelector('#location_temp');
        location.style.display = 'block';
    },
    // Click function of close button state and city is appended in location field.
    _onCloseClick(ev) {
        console.log(location, 'locationnnn before')
        var location = this.el.querySelector('#location_temp');
        var city = this.el.querySelector('#city_id').value
        var state = this.el.querySelector("#state_id");
        this.el.querySelector('#location_id').value = state.selectedOptions[0].text + ',' + city
        console.log(location, 'locationnnn')
        location.style.display = 'none';
    },
    // date validation in Subscription form.
    _onNextClick(e) {
        console.log(e, 'startdateee')
        var start = this.el.querySelector('#start_date').value;
        var end = this.el.querySelector('#end_date').value;
        if (start > end) {
            e.preventDefault();
            alert('The Start Date must be earlier than the End Date!!!!!!!!!');
        }
    }
})
