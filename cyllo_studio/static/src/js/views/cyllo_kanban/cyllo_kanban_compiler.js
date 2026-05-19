/** @odoo-module **/

import {
    append,
    combineAttributes,
    createElement,
    extractAttributes,
    getTag,
} from "@web/core/utils/xml";
import {toStringExpression} from "@web/views/utils";
import {toInterpolatedStringExpression, ViewCompiler} from "@web/views/view_compiler";
import {KanbanCompiler} from "@web/views/kanban/kanban_compiler";
import { patch } from "@web/core/utils/patch";


/**
 * @typedef {Object} DropdownDef
 * @property {Element} el
 * @property {boolean} inserted
 * @property {boolean} shouldInsexrt
 * @property {("dropdown" | "toggler" | "menu")[]} parts
 */


export class CylloKanbanCompiler extends KanbanCompiler {
    setup() {
        super.setup();
        this.isKanbanView = true
    }



    compileField(el, params) {
        console.log("CmplFieldssss", el, params)
        const compiled = super.compileField(el, params);
         if (!el.hasAttribute("widget")) {
            const path = el.getAttribute('cy-xpath')
            const name = el.getAttribute('name')
            compiled.setAttribute('cy-xpath', path)
            compiled.setAttribute('name', name)
            compiled.setAttribute('field-tag', true)
            compiled.setAttribute("t-on-click.self", `(el)=>__comp__.handleSelectField(el)`)
         }
        return compiled
    }

compileNode(node, params = {}, evalInvisible = true) {
    let compiledNode = super.compileNode(node, params, evalInvisible);
    const validAttributes = ["t-out", "t-esc"];
    if (compiledNode?.attributes) {
        const AttrArray = Array.from(compiledNode.attributes);
        const hasValidAttribute = validAttributes.some(attr =>
            AttrArray.some(nodeAttr => nodeAttr.name === attr)
        );
          if (compiledNode.tagName.toLowerCase() === 'span') {
                compiledNode.setAttribute("t-on-click", `(el)=>__comp__.handleSelectSpan(el)`);
            }
        if (hasValidAttribute) {
            AttrArray.forEach(nodeAttr => {
                if (validAttributes.includes(nodeAttr.name)) {
                    const match = nodeAttr.value.match(/record\.([^.]+)\.value/);
                    if (match) {
                        const extractedValue = match[1];
                        compiledNode.setAttribute('name', extractedValue);
                    }
                }
            });
            if (compiledNode.tagName.toLowerCase() === 't') {
                const span = document.createElement('span');
                Array.from(compiledNode.attributes).forEach(attr => {
                    span.setAttribute(attr.name, attr.value);
                });
                while (compiledNode.firstChild) {
                    span.appendChild(compiledNode.firstChild);
                }
                compiledNode = span;
            }
            compiledNode.setAttribute("t-on-click", `(el)=>__comp__.handleSelectField(el)`);
        }
    }
    return compiledNode;
}
}
CylloKanbanCompiler.OWL_DIRECTIVE_WHITELIST = [
    ...KanbanCompiler.OWL_DIRECTIVE_WHITELIST,
];

patch(KanbanCompiler.prototype,{
    compileButton(el, params){
        const compiled = super.compileButton(el, params)
        if(compiled.hasAttribute('t-on-click')){
            compiled.setAttribute('t-on-click','()=>{}')
        }
        return compiled
    }
})
