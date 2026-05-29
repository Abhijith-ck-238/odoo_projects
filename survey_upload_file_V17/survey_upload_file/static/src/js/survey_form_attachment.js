/** @odoo-module */
import publicWidget from "@web/legacy/js/public/public_widget";
import SurveyFormWidget from '@survey/js/survey_form';
import SurveyPreloadImageMixin from "@survey/js/survey_preload_image_mixin";
/**  Extends publicWidget to create "SurveyFormUpload" */
publicWidget.registry.SurveyFormUpload = publicWidget.Widget.extend(SurveyPreloadImageMixin, {
        selector: '.o_survey_form',
        events: {
            'change .o_survey_upload_file': '_onFileChange',
        },
        init() {
            this._super(...arguments);
            this.rpc = this.bindService("rpc");
        },
       _onFileChange: function (ev) {
            const inputEl = ev.currentTarget;
            const files = ev.target.files;
            Object.entries(files).forEach(([key, value]) => {
            });
            if (!files || files.length === 0) return;

            var fileList = document.getElementById('fileList');
            var existingUl = fileList.querySelector('ul')
            if(existingUl){

                Object.entries(files).forEach(([key, value]) => {
                    const exists = Array.from(existingUl.children).some(
                        (li) => li.textContent === value.name
                    );
                    if(!exists){
                        var li = document.createElement('li');
                        li  .textContent = value.name;
                        existingUl.appendChild(li);
                    }
                });
            }
            else{
                var ul = document.createElement('ul');
                Object.entries(files).forEach(([key, value]) => {
                    var li = document.createElement('li');
                    li.textContent = value.name;
                    ul.appendChild(li);
                });
                fileList.appendChild(ul);
            }

            const readFile = (file) => {
                return new Promise((resolve, reject) => {
                    const reader = new FileReader();
                    reader.onload = () => {
                        const base64 = reader.result.split(',')[1];
                        resolve({
                            data: base64,
                            name: file.name
                        });
                    };
                    reader.onerror = reject;
                    reader.readAsDataURL(file);
                });
            };


            Promise.all([...files].map(readFile)).then(results => {
                inputEl.getAttribute('data-oe-data') && results.concat(JSON.parse(inputEl.getAttribute('data-oe-data')))
                inputEl.setAttribute('data-oe-data', JSON.stringify(results));
            });
        }

    });
export default publicWidget.registry.SurveyFormUpload;
