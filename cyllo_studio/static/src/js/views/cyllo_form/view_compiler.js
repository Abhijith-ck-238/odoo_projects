/** @odoo-module **/
import { FormCompiler } from "@web/views/form/form_compiler";
import { SIZES } from "@web/core/ui/ui_service";
import { InnerGroup, OuterGroup, Group } from "@web/views/form/form_group/form_group";
import { toStringExpression } from "@web/views/utils";
import { useService } from "@web/core/utils/hooks";
import { registry } from "@web/core/registry";
import { evaluateExpr } from "@web/core/py_js/py";

import {
    append,
    combineAttributes,
    createElement,
    createTextNode,
    getTag,
    setAttributes,
} from "@web/core/utils/xml";
import {
    copyAttributes,
    getModifier,
    isComponentNode,
    isTextNode,
    makeSeparator,
} from "@web/views/view_compiler";

//function isComment(node) {
//    return node.nodeType === 8;
//}

/**
 * @param {Record<string, any>} obj
 * @returns {string}
 */
export function objectToString(obj) {
    return `{${Object.entries(obj)
        .map((t) => t.join(":"))
        .join(",")}}`;
}
 function appendAttf(el, attr, string) {
    const attrKey = `t-attf-${attr}`;
    const attrVal = el.getAttribute(attrKey);
    el.setAttribute(attrKey, appendToExpr(attrVal, string));
}
//
function appendToExpr(expr, string) {
    const re = /{{.*}}/;
    const oldString = re.exec(expr);
    return oldString ? `${oldString} {{${string} }}` : `{{${string} }}`;
}

function XpathExtract(el, tag) {
    var parser = new DOMParser();
    var xmlDoc = parser.parseFromString(el.outerHTML, "text/xml");
    var elements = xmlDoc.evaluate(tag, xmlDoc, null, XPathResult.ANY_TYPE, null);
    var element = elements.iterateNext();
    var xpath = '';
    for (; element && element.nodeType == 1; element = element.parentNode) {
        var id = element.getAttribute('id');
        if (id) {
            xpath = '[@id="' + id + '"]' + xpath;
            break;
        }

        var nodeName = element.nodeName.toLowerCase();
        var parent = element.parentNode;
        var siblings = parent.childNodes;
        var count = 0;
        for (var i = 0; i < siblings.length; i++) {
            var sibling = siblings[i];
            if (sibling.nodeType == 1 && sibling.nodeName.toLowerCase() == nodeName) {
                count++;
            }
            if (sibling == element) {
                xpath = '/' + nodeName + '[' + count + ']' + xpath;
                break;
            }
        }
    }
    return xpath

}


export class CylloFormCompiler extends FormCompiler {
    setup() {
        super.setup();
        this.rpc = useService("rpc");
    }

    compileField(el, params) {
        const field = super.compileField(el, params);
        const fieldName = el.getAttribute("name");
        const fieldString = el.getAttribute("string");
        const fieldId = el.getAttribute("field_id");
        const contextViewRef = el.getAttribute("context");
        const labelsForAttr = el.getAttribute("id") || fieldName;
        const labels = this.getLabels(labelsForAttr);
        const dynamicLabel = (label) => {
            const formLabel = this.createLabelFromField(fieldId, fieldName, fieldString, label, {
                ...params,
                currentFieldArchNode: el,
            });
            if (formLabel) {
                label.replaceWith(formLabel);
            } else {
                label.remove();
            }
            return formLabel;
        };
        for (const label of labels) {
            dynamicLabel(label);
        }
        this.encounteredFields[fieldName] = dynamicLabel;
        return field;
    }

    compileForm(el, params) {
        this.formView = el
        localStorage.setItem('elouterHTML',this.formView.outerHTML)
        const sheetNode = el.querySelector("sheet");
        const displayClasses = sheetNode
            ? `d-flex {{ __comp__.uiService.size < ${SIZES.XXL} ? "flex-column" : "flex-nowrap h-100" }}`
            : "d-block";
        const stateClasses =
            "{{ __comp__.props.record.dirty ? 'o_form_dirty' : !__comp__.props.record.isNew ? 'o_form_saved' : '' }}";
        const form = createElement("div", {
            class: "o_form_renderer",
            "t-att-class": "__comp__.props.class",
            "t-attf-class": `{{__comp__.props.record.isInEdition ? 'o_form_editable' : 'o_form_readonly'}} ${displayClasses} ${stateClasses}`,
            "cy-xpath": el.getAttribute("cy-xpath"),
        });
        if (!sheetNode) {
            for (const child of el.childNodes) {
                // ButtonBox are already compiled for the control panel and should not
                // be recompiled for the renderer of the view
                if (child.attributes?.name?.value !== "button_box") {
                    append(form, this.compileNode(child, params));
                }
            }
            form.classList.add("o_form_nosheet");
        }
        else {
            var hasChatter = false
            const chatter = createElement('ChatterComponent',{
                    viewId: `__comp__.env.config.viewId`,
                    model: `__comp__.env.model.config.resModel`,
                });
            let compiledList = [];
            for (const child of el.childNodes) {
                const compiled = this.compileNode(child, params);
                if (getTag(child, true) === "sheet") {
                    append(form, compiled);
                    compiled.prepend(...compiledList);
                    compiledList = [];
                }
                else if (compiled) {
                    if (child.classList?.contains('oe_chatter')) {
                        hasChatter = true
                        const path = child.getAttribute("cy-xpath")
                        chatter.setAttribute('path', toStringExpression(path))
                        chatter.setAttribute('hasChatter', hasChatter)
                        compiledList.push(chatter)
                    } else {
                        compiledList.push(compiled);
                    }
                        compiledList.push(compiled);
                }
            }
            const preview = el.querySelector('.o_attachment_preview')
            if(preview){
                 chatter.setAttribute('preview', true)
                compiledList.push(chatter)
            }
            if(!hasChatter){
                chatter.setAttribute('hasChatter', hasChatter)
                compiledList.push(chatter)
            }

            append(form, compiledList);
        }
        return form;
    }

    /**
     * @param {Element} el
     * @param {Record<string, any>} params
     * @returns {Element}
     */
    compileHeader(el, params) {
        const statusBar = createElement("div");
        statusBar.className =
            "o_form_statusbar position-relative d-flex justify-content-between mb-0 mb-md-2 pb-2 pb-md-0";
        statusBar.setAttribute("cy-xpath", el.getAttribute('cy-xpath'));
        statusBar.setAttribute("studio-header", el.getAttribute('studio-header') || "");
        const buttons = [];
        const others = [];
        const hasStatusBar = el.getAttribute('status-bar') || false
        for (const child of el.childNodes) {
            const compiled = this.compileNode(child, params);
            if (!compiled || isTextNode(compiled)) {
                continue;
            }
            if (getTag(child, true) === "field") {
                compiled.setAttribute("showTooltip", true);
                others.push(compiled);
            } else {
                if (compiled.tagName === "ViewButton") {
                    compiled.setAttribute("defaultRank", "'btn-secondary'");
                }
                buttons.push(compiled);
            }
        }
        if (!hasStatusBar) {
            const addStatusBar = createElement('StatusBar',{
                fields: `__comp__.props.record.fields`,
                viewId: `__comp__.env?.config.viewId`,
                model: `__comp__.env?.model.config.resModel`,
            })
            const path = el.getAttribute("cy-xpath")
            // @fixme: Error occurs when studio reloads (sometimes). Don't remove the below console statement; need to debug.
            console.log("Minnale effect error", path)
            console.log("Minnale effect error 123", el)
            addStatusBar.setAttribute("path", toStringExpression(path))
            addStatusBar.setAttribute("header", toStringExpression(el.getAttribute('studio-header') || ""))
            others.push(addStatusBar);
        }
        let slotId = 0;
        const statusBarButtons = createElement("StatusBarButtons");
        for (const button of buttons) {
            const slot = createElement("t", {
                "t-set-slot": `button_${slotId++}`,
                isVisible: button.getAttribute("t-if") || true,
            });
            append(slot, button);
            append(statusBarButtons, slot);
        }
        append(statusBar, statusBarButtons);
        append(statusBar, others);
        return statusBar;
    }



        compileGroup(el, params) {
            const isOuterGroup = [...el.children].some((c) => getTag(c, true) === "group");
            const formGroup = createElement(isOuterGroup ? "OuterGroup" : "InnerGroup");
            let slotId = 0;
            let sequence = 0;

            if (el.hasAttribute("col")) {
                formGroup.setAttribute("maxCols", el.getAttribute("col"));
            }

            if (el.hasAttribute("string")) {
                const titleSlot = createElement("t", { "t-set-slot": "title" }, [
                    makeSeparator(el.getAttribute("string")),
                ]);
                append(formGroup, titleSlot);
            }

            let forceNewline = false;

            for (const child of el.children) {
                if (getTag(child, true) === "newline") {
                    forceNewline = true;
                    continue;
                }

                const invisible = getModifier(child, "invisible");
                const invisible_session =  sessionStorage.getItem('invisible');
                if(!invisible_session){
                    if (!params.compileInvisibleNodes && (invisible === "True" || invisible === "1")) {
                        continue;
                    }
                }

                const mainSlot = createElement("t", {
                    "t-set-slot": `item_${slotId++}`,
                    type: "'item'",
                    sequence: sequence++,
                    "t-slot-scope": "scope",
                });
                let itemSpan = parseInt(child.getAttribute("colspan") || "1", 10);

                if (forceNewline) {
                    mainSlot.setAttribute("newline", true);
                    forceNewline = false;
                }

                if (getTag(child, true) === "separator") {
                    itemSpan = parseInt(formGroup.getAttribute("maxCols") || 2, 10);
                }

                if (child.matches("div[class='clearfix']:empty")) {
                    itemSpan = parseInt(formGroup.getAttribute("maxCols") || 2, 10);
                }

                let slotContent;
                  if (getTag(child, true) === "field") {
                  const addLabel = child.hasAttribute("nolabel")
                        ? child.getAttribute("nolabel") !== "1"
                        : true;
                    slotContent = this.compileNode(child, { ...params, currentSlot: mainSlot }, false);
                    if (slotContent && addLabel && !isOuterGroup && !isTextNode(slotContent)) {
                        itemSpan = itemSpan === 1 ? itemSpan + 1 : itemSpan;
                        const fieldName = child.getAttribute("name");
                        const fieldId = slotContent.getAttribute("id") || fieldName;
                        const props = {
                            id: `${fieldId}`,
                            fieldName: `'${fieldName}'`,
                            record: `__comp__.props.record`,
                            string: child.hasAttribute("string")
                                ? toStringExpression(child.getAttribute("string"))
                                : `__comp__.props.record.fields.${fieldName}.string`,
                            fieldInfo: `__comp__.props.archInfo.fieldNodes[${fieldId}]`,
                        };
                        mainSlot.setAttribute("props", objectToString(props));
                        mainSlot.setAttribute("Component", "__comp__.constructor.components.FormLabel");
                        mainSlot.setAttribute("subType", "'item_component'");
                        mainSlot.setAttribute("cy-xpath", `'${child.getAttribute("cy-xpath")}'`);
                    } else {
                    }
                } else {
                    if (getTag(child, true) === "div" && child.children[0] ) {

                        for(const element of child.children){
                            if(getTag(element, true) === "span"){
                                const spanInvisible = toStringExpression(element.getAttribute('invisible') || '0')
                                element.setAttribute("t-on-click", `(ev)=>__comp__.onSpanClick(ev, ${spanInvisible})`)
                                element.setAttribute("t-att-class", `__comp__.evaluateBooleanExpr(${JSON.stringify(
                                                                        getModifier(element, "invisible")
                                                                    )},__comp__.props.record.evalContextWithVirtualIds)
                                                                    ? 'cy-studio-striped' : ''`)
                            }
                        }

                        mainSlot.setAttribute("cy-xpath", `'${child.children[0].getAttribute("cy-xpath")}'`);
                    }
                    // TODO: When every apps will be revamp, we could remove the condition using 'o_td_label' in favor of 'o_wrap_label'
                    if (
                        child.classList.contains("o_wrap_label") ||
                        child.classList.contains("o_td_label") ||
                        getTag(child, true) === "label"
                    ) {
                        if(child.hasAttribute("striped")){
                            mainSlot.setAttribute("striped", "'cy-studio-striped'")
                        }
                        mainSlot.setAttribute("subType", "'label'");
                        child.classList.remove("o_wrap_label");
                        mainSlot.setAttribute("cy-xpath", `'${child.getAttribute("cy-xpath")}'`);
                    }
                    slotContent = this.compileNode(child, { ...params, currentSlot: mainSlot }, false);
                }

                if (slotContent && !isTextNode(slotContent)) {
                    let isVisibleExpr;
                    if (!invisible || invisible === "False" || invisible === "0") {
                        isVisibleExpr = "true";
                    } else if (invisible === "True" || invisible === "1") {
                        isVisibleExpr = "false";
                    } else {
                        isVisibleExpr = `!__comp__.evaluateBooleanExpr(${JSON.stringify(
                            invisible
                        )},__comp__.props.record.evalContextWithVirtualIds)`;
                    }
                    const invisible_session =  sessionStorage.getItem('invisible');
                    if(invisible_session){
                        mainSlot.setAttribute("invisibleStriped", `!${isVisibleExpr}`)
                        mainSlot.setAttribute("isVisible", true);
                    }else{
                        mainSlot.setAttribute("isVisible", isVisibleExpr);
                    }
                    if (itemSpan > 0) {
                        mainSlot.setAttribute("itemSpan", `${itemSpan}`);
                    }

                    const groupClassExpr = `scope && scope.className`;
                    if (isComponentNode(slotContent)) {
                        if (getTag(slotContent) === "FormLabel") {
                            mainSlot.prepend(
                                createElement("t", {
                                    "t-set": "addClass",
                                    "t-value": groupClassExpr,
                                })
                            );
                            combineAttributes(
                                slotContent,
                                "className",
                                `(addClass ? " " + addClass : "")`,
                                `+`
                            );
                        } else if (getTag(child, true) !== "button") {
                            if (slotContent.hasAttribute("class")) {
                                mainSlot.prepend(
                                    createElement("t", {
                                        "t-set": "addClass",
                                        "t-value": groupClassExpr,
                                    })
                                );
                                combineAttributes(
                                    slotContent,
                                    "class",
                                    `(addClass ? " " + addClass : "")`,
                                    `+`
                                );
                            } else {
                                slotContent.setAttribute("class", groupClassExpr);
                            }
                        }
                    } else {
                        appendAttf(slotContent, "class", `${groupClassExpr} || ""`);
                    }
                    append(mainSlot, slotContent);
                    append(formGroup, mainSlot);
                }
            }
            var GroupPath = el.getAttribute('cy-xpath')
            formGroup.setAttribute("cy-xpath", `'${GroupPath}'`);

            return formGroup;
    }



    createLabelFromField(fieldId, fieldName, fieldString, label, params) {
        let labelText = label.textContent || fieldString;
        let cyXpath = ''
        if(label.hasAttribute("cyXpath")){
            cyXpath = toStringExpression(label.getAttribute("cyXpath"))
        }

        if (label.hasAttribute("data-no-label")) {
            labelText = toStringExpression("");
        } else {
            labelText = labelText
                ? toStringExpression(labelText)
                : `__comp__.props.record.fields['${fieldName}'].string`;
        }
        const formLabel = createElement("FormLabel", {
            id: `'${fieldId}'`,
            fieldName: `'${fieldName}'`,
            record: `__comp__.props.record`,
            fieldInfo: `__comp__.props.archInfo.fieldNodes['${fieldId}']`,
            className: `"${label.className}"`,
            string: labelText,
            cyXpath: cyXpath,
        });
        const condition = label.getAttribute("t-if");
        if (condition) {
            formLabel.setAttribute("t-if", condition);
        }
        return formLabel;
    }

     /**
     * @param {Element} el
     * @param {Record<string, any>} params
     * @returns {Element}
     */
    compileLabel(el, params) {
        const forAttr = el.getAttribute("for");
        // A label can contain or not the labelable Element it is referring to.
        // If it doesn't, there is no `for=`
        // Otherwise, the targetted element is somewhere else among its nextChildren
        if (forAttr) {
            let label = createElement("label");
            copyAttributes(el, label);
            const string = el.getAttribute("string");
            if (string) {
                append(label, createTextNode(string));
            } else if (string === "") {
                label.setAttribute("data-no-label", "true");
            }
            if(getTag(label, true) === "label"){
                label.setAttribute("cyXpath", el.getAttribute("cy-xpath") || '');
            }
            if (this.encounteredFields[forAttr]) {
                label = this.encounteredFields[forAttr](label);
            } else {
                this.pushLabel(forAttr, label);
            }

            return label;
        }
        const res = this.compileGenericNode(el, params);
        copyAttributes(el, res);
        return res;
    }



    compileNotebook(el, params) {
        const invisible_session =  sessionStorage.getItem('invisible');
        const noteBookId = this.noteBookId++;
        const noteBook = createElement("Notebook");
        const pageAnchors = [...document.querySelectorAll("[href^=\\#]")]
            .map((a) => CSS.escape(a.getAttribute("href").substring(1)))
            .filter((a) => a.length);
        const noteBookAnchors = {};

        if (el.hasAttribute("class")) {
            noteBook.setAttribute("className", toStringExpression(el.getAttribute("class")));
            el.removeAttribute("class");
        }

        noteBook.setAttribute(
            "defaultPage",
            `__comp__.props.record.isNew ? undefined : __comp__.props.activeNotebookPages[${noteBookId}]`
        );
        noteBook.setAttribute(
            "onPageUpdate",
            `(page) => __comp__.props.onNotebookPageChange(${noteBookId}, page)`
        );
        noteBook.setAttribute('cyXpath', toStringExpression(el.getAttribute("cy-xpath") || ""))
        for (const child of el.children) {
            if (getTag(child, true) !== "page") {
                continue;
            }
            const invisible = getModifier(child, "invisible");
            if(!invisible_session){
                if (!params.compileInvisibleNodes && (invisible === "True" || invisible === "1")) {
                    continue;
                }
            }


            const pageSlot = createElement("t");
            append(noteBook, pageSlot);

            const pageId = `page_${this.id++}`;
            const pageTitle = toStringExpression(
                child.getAttribute("string") || child.getAttribute("name") || ""
            );
            const pageNodeName = toStringExpression(child.getAttribute("name") || "");

            pageSlot.setAttribute("t-set-slot", pageId);
            pageSlot.setAttribute("title", pageTitle);
            pageSlot.setAttribute("name", pageNodeName);
            pageSlot.setAttribute("cyXpath", toStringExpression(child.getAttribute("cy-xpath") || ""));
            pageSlot.setAttribute("groups", toStringExpression(child.getAttribute("groups") || ""));
            pageSlot.setAttribute("autofocus", toStringExpression(child.getAttribute("autofocus") || ""));
            pageSlot.setAttribute("invisible", toStringExpression(invisible || "False"));

            if (child.hasAttribute("striped")){
                child.classList.add('cy-studio-striped')
            }

            if (child.className) {
                pageSlot.setAttribute("className", `"${child.className}"`);
            }

            if (child.getAttribute("autofocus") === "autofocus") {
                noteBook.setAttribute(
                    "defaultPage",
                    `__comp__.props.record.isNew ? "${pageId}" : (__comp__.props.activeNotebookPages[${noteBookId}] || "${pageId}")`
                );
            }

            for (const anchor of child.querySelectorAll("[href^=\\#]")) {
                const anchorValue = CSS.escape(anchor.getAttribute("href").substring(1));
                if (!anchorValue.length) {
                    continue;
                }
                pageAnchors.push(anchorValue);
                noteBookAnchors[anchorValue] = {
                    origin: `'${pageId}'`,
                };
            }

            let isVisibleExpr;
            if (!invisible || invisible === "False" || invisible === "0") {
                isVisibleExpr = "true";
            } else if (invisible === "True" || invisible === "1") {
                isVisibleExpr = "false";
            } else {
                isVisibleExpr = `!__comp__.evaluateBooleanExpr(${JSON.stringify(
                    invisible
                )},__comp__.props.record.evalContextWithVirtualIds)`;
            }
            if(invisible_session){
                pageSlot.setAttribute("isVisible", true);
                pageSlot.setAttribute("invisibleStriped", `!${isVisibleExpr}`)
            }else{
            pageSlot.setAttribute("isVisible", isVisibleExpr);
            }

            for (const contents of child.children) {
                append(pageSlot, this.compileNode(contents, { ...params, currentSlot: pageSlot }));
            }
        }

        if (pageAnchors.length) {
            // If anchors from the page are targetting an element
            // present in the notebook, it must be aware of the
            // page that contains the corresponding element
            for (const anchor of pageAnchors) {
                let pageId = 1;
                for (const child of el.children) {
                    if (child.querySelector(`#${anchor}`)) {
                        noteBookAnchors[anchor].target = `'page_${pageId}'`;
                        noteBookAnchors[anchor] = objectToString(noteBookAnchors[anchor]);
                        break;
                    }
                    pageId++;
                }
            }
            noteBook.setAttribute("anchors", objectToString(noteBookAnchors));
        }

        return noteBook;
    }

     /**
     * @param {Element} el
     * @param {Record<string, any>} params
     * @returns {Element}
     */
    compileButtonBox(el, params) {
        if (!el.children.length) {
            return this.compileGenericNode(el, params);
        }

        el.classList.remove("oe_button_box");
        const buttonBox = createElement("ButtonBox");
        buttonBox.setAttribute("t-if", "!__comp__.env.inDialog");
        buttonBox.setAttribute("cyXpath", toStringExpression(el.getAttribute("cy-xpath") || ""))
        let slotId = 0;
        let hasContent = false;
        for (const child of el.children) {
            const invisible = getModifier(child, "invisible");
            if (!params.compileInvisibleNodes && (invisible === "True" || invisible === "1")) {
                continue;
            }
            hasContent = true;
            let isVisibleExpr;
            if (!invisible || invisible === "False" || invisible === "0") {
                isVisibleExpr = "true";
            } else if (invisible === "True" || invisible === "1") {
                isVisibleExpr = "false";
            } else {
                isVisibleExpr = `!__comp__.evaluateBooleanExpr(${JSON.stringify(
                    invisible
                )},__comp__.props.record.evalContextWithVirtualIds)`;
            }
            let mainSlot = ""
            const invisible_session =  sessionStorage.getItem('invisible');
              mainSlot = createElement("t", {
            "t-set-slot": `slot_${slotId++}`,isVisible: invisible_session ? true : isVisibleExpr,
            });
            if (child.getAttribute('string')) {
                child.setAttribute('string', child.getAttribute('string') || "")
                child.setAttribute('stringPath', child.getAttribute('cy-xpath') || "")
            } else if (child.firstElementChild?.tagName === 'field') {
                child.setAttribute('string', child.firstElementChild.getAttribute('string') || "")
                child.setAttribute('stringPath', child.firstElementChild.getAttribute('cy-xpath') || "")
                child.setAttribute('StatusLabelPath', child.querySelector('[status_label]')?.getAttribute('cy-xpath') || false)
            } else {
                child.setAttribute('string', child.querySelector('.o_stat_text')?.textContent.trim() || "")
                child.setAttribute('stringPath', child.querySelector('.o_stat_text')?.getAttribute('cy-xpath') || "")
            }

            if (child.tagName === "button" || child.children.tagName === "button") {
                child.classList.add(
                    "oe_stat_button",
                    "btn",
                    "btn-outline-secondary",
                    "flex-grow-1",
                    "flex-lg-grow-0"
                );
            }
            if (child.tagName === "field") {
                child.classList.add("d-inline-block", "mb-0", "z-index-0");
            }
            if (invisible_session ){
                const compileNode = this.compileNode(child, params, false)
                compileNode.setAttribute('striped', `!${isVisibleExpr}`)
                append(mainSlot, compileNode);
            } else {
                append(mainSlot, this.compileNode(child, params, false));
            }
            append(buttonBox, mainSlot);
        }

        return hasContent ? buttonBox : "";
    }


    compileSheet(el, params) {
        const sheetBG = createElement("div");
        sheetBG.className = "o_form_sheet_bg";

        const sheetFG = createElement("div");
        sheetFG.className = "o_form_sheet position-relative";
        sheetFG.setAttribute("cy-xpath", el.getAttribute("cy-xpath"));
        const newSheet = el.getAttribute("sheet");
        if(newSheet){
            sheetFG.setAttribute("sheet", newSheet);
        }
        append(sheetBG, sheetFG);
        var title_count = 0
        var badge_count = 0
        var ribbon_count = 0
        var avatar_count = 0
        for (const child of el.childNodes) {
           if (getTag(child, true) == "widget") {
                ribbon_count ++;
           }
           if (getTag(child, true) === "div") {
                if(child.className.includes('oe_title')){
                    title_count ++;
                }
                if(child.className.includes('badge')){
                    badge_count ++;
                }
            }
            if (getTag(child, true) === "field") {
                if (child.className.includes('oe_avatar')) {
                    avatar_count ++
                }
            }
        }
        for (const child of el.childNodes) {
            const compiled = this.compileNode(child, params);
            let hasAvatar = el.getAttribute('avatar') || false
            if (!badge_count && !ribbon_count && !avatar_count && !hasAvatar){

                var path = child.nextElementSibling?.children[0]?.classList.contains('button-box-container') ? child.parentElement.firstElementChild.nextElementSibling?.getAttribute("cy-xpath")    : child.nextElementSibling?.getAttribute("cy-xpath")
                if(!path){
                    if(child.nodeType === 1){
                        path =  child.previousElementSibling?.children[0]?.classList.contains('button-box-container') ? child.previousElementSibling.parentElement.firstElementChild.nextElementSibling?.getAttribute("cy-xpath")    : child.previousElementSibling?.getAttribute("cy-xpath")
                    }
                }
                if(path){
                     const Avatar = createElement('AvatarComponent',{
                        fields: `__comp__.props.record.fields`,
                        viewId: `__comp__.env.config.viewId`,
                        model: `__comp__.env.model.config.resModel`,
                    });
                    Avatar.setAttribute("path", toStringExpression(path))
                    avatar_count = 1
                    append(sheetFG, Avatar)
                }


            }
            if (!compiled) {
                continue;
            }
            if (compiled.nodeName === "ButtonBox") {
                // in form views with a sheet, the button box is moved to the
                // control panel, and in dialogs, there's no button box
                continue;
            }
            if (getTag(child, true) === "field") {
                compiled.setAttribute("showTooltip", true);
            }
            if (getTag(child, true) == "widget") {
                ribbon_count --;
            }
            if (getTag(child, true) === "div") {

                if(child.className.includes('oe_title')){
                    title_count--;
                }
                if(child.className.includes('badge')){
                    badge_count --;
                }
            }
            append(sheetFG, compiled);

        }
        return sheetBG;
    }

    compileButton(el, params) {
        return super.compileButton(el, params)
    }


}


