/** @odoo-module **/
import SurveyFormWidget from "@survey/js/survey_form";

SurveyFormWidget.include({
    events: Object.assign({}, SurveyFormWidget.prototype.events, {
        'input .o_survey_question_numerical_box': '_attachNumericalInputListeners',
    }),
    start: function () {
        this._super.apply(this, arguments);

        let submitButton = document.querySelector("button[type='submit']");
        if (submitButton && !this.options.isStartScreen) {
            submitButton.addEventListener("click", function () {
                sessionStorage.setItem("survey_sum",0);
            });
        }
     },


    _attachNumericalInputListeners: function () {
        var self = this;
        document.querySelectorAll('.o_survey_question_numerical_box').forEach(function (input) {
            input.addEventListener('input', function () {
                self._updateSum();
            });
//        });
    },

    _updateSum: function () {
        var self = this;

        // Get the accumulated sum from previous pages
        var previousSum = parseFloat(sessionStorage.getItem("survey_sum")) || 0;

        // Calculate sum only from current page inputs
        var currentPageSum = 0;
        document.querySelectorAll('.o_survey_question_numerical_box').forEach(function (input) {
            var number = parseFloat(input.value) || 0;
            currentPageSum += number;
        });

        // Total sum = previous pages + current page
        self.sum = previousSum + currentPageSum;

        // Update display
        var sumValueSpan = document.querySelector('.sum-value');
        if (sumValueSpan) {
            sumValueSpan.textContent = self.sum;
        }
    },

    _prepareSubmitValues: function (formData, params) {
        var self = this;

        // Ensure sum is up to date before submission
        this._updateSum();

        // Store ONLY current page sum before moving to next page
        var currentPageSum = 0;
        document.querySelectorAll('.o_survey_question_numerical_box').forEach(function (input) {
            currentPageSum += parseFloat(input.value) || 0;
        });
        sessionStorage.setItem("survey_sum",
            (parseFloat(sessionStorage.getItem("survey_sum")) || 0) + currentPageSum
        );

        // Call parent method
        this._super(formData, params);

        // Add sum to params
        params.sum = self.sum;
    },
});
