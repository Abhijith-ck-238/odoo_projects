odoo.define('logistics.clickable_many2many', function (require) {
    "use strict";
    var relational_fields = require('web.relational_fields');
    var fieldRegistry = require('web.field_registry')    
    var ajax = require('web.ajax');

    var clickable_many2many = relational_fields.FieldMany2ManyTags.extend({
        _render: function () {
            var self = this;
            console.log("ssssssssssssssssssssssssss",self)
    
            if (this.$el) {
                this.$el.empty().addClass('o_field_many2manytags o_kanban_tags');
            }
    
            _.each(this.value.data, function (m2m) {
                if (self.colorField in m2m.data && !m2m.data[self.colorField]) {
                    return;
                }
    
                $('<span>', {
                    class: 'o_tag o_tag_color_' + (m2m.data[self.colorField] || 0),
                    text: m2m.data.display_name,
                })
                .prepend('<span>')
                .appendTo(self.$el);
            });
            self.$el.each((index)=>{
                let o_tag_elements = self.$el[index].querySelectorAll(".o_tag");
                for(let c=0;c<o_tag_elements.length;c++){
                    o_tag_elements[c].addEventListener("click",(e)=>{
                        let po_name = o_tag_elements[c].innerHTML.replace("<span></span>","").split(" (")[0];
                        console.log(po_name)
                        let customer = self.$el[index].parentNode.parentNode.querySelector(".sh_t_customer span").innerHTML;
                        pUpLogic(po_name,customer,ajax);
                    })
                }
            })
        },
    });

    fieldRegistry.add('clickable_many2many', clickable_many2many);
    return clickable_many2many;
});

const strToHtml = (str_element) => {
    var parser = new DOMParser();
    var doc = parser.parseFromString(str_element, 'text/html');
    return doc.body.firstChild;
}

const getRemoteElement = (file_name, cb) => {
    file_path = `/logistics/static/src/html/${file_name}.html`
    $.get(file_path,(str_element)=>{
        const node_element = strToHtml(str_element)
        cb(node_element);
    })
}

function insertAfter(newNode, existingNode) {
    existingNode.parentNode.insertBefore(newNode, existingNode.nextSibling);
}

const query = (ajax, model, method, args, cb)=>{
    ajax.jsonRpc('/web/dataset/call_kw', 'call', {
        'model': model,
        'method': method,
        'args': args,
        'kwargs': {
            'context': {},
        }
    }).then(cb);
}


const pUpLogic = (po_name,customer,ajax) => {
    getRemoteElement('pup',(pup_element)=>{
        const body = document.querySelector('body')
        insertAfter(pup_element, body)
        query(ajax, "logistics.shipment", "get_po_info", [po_name], (po_info)=>{
            getRemoteElement("info_container",(po_info_element)=>{
                document.querySelector(".sh_t_loading").parentNode.replaceChild(po_info_element, document.querySelector(".sh_t_loading"));
                document.querySelector(".sh_t_customer-value").innerHTML = customer;
                const info_lines = (cols) => `<div class="sh_t_po-info">${cols}</div>`
                let info_line_elements = "";
                for(let c=0;c<po_info.length;c++){
                    let cols = ""
                    for(const key in po_info[c]){
                        cols += `<span>${po_info[c][key]}</span>`
                    }
                    info_line_elements += info_lines(cols);
                }
                document.querySelector(".sh_t_po-info-lines").innerHTML = info_line_elements;
                document.querySelector(".sh_t__cross_section span").addEventListener("click",()=>{
                    document.querySelector(".sh_t_black-screen").parentElement.removeChild(document.querySelector(".sh_t_black-screen"));
                })
            })
        })
    })
}
    


