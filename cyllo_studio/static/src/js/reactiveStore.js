///** @odoo-module */
//import {registry} from "@web/core/registry";
//import {reactive, EventBus, useComponent, useState} from "@odoo/owl";
//import {useService} from "@web/core/utils/hooks";
//export const store = {
//
//}
//export const reactiveStore = {
//    store: reactive(store), // Initialize a reactive store object
//    bus: new EventBus(),
//    setState: (state) => {
//        Object.assign(reactiveStore.store, state);
//        reactiveStore.bus.trigger("update", state);
//    },
//
//    start(env) {
//        return {
//            bus: reactiveStore.bus,
//            store: reactiveStore.store,
//            setState: reactiveStore.setState
//        };
//    }
//};
//
//registry.category("services").add("reactiveStore", reactiveStore);
//
//export function useReactiveStore() {
//    const reactiveStoreService = useService("reactiveStore");
//    const component = useComponent()
//    const localState = useState({...reactiveStoreService.store});
//
//    const updateHandler = () => {
//        Object.assign(localState, reactiveStoreService.store);
//        component.render()
//    };
//    reactiveStoreService.bus.addEventListener("update", updateHandler);
//
//    return {
//        store: localState,
//        setState: reactiveStoreService.setState
//    };
//}