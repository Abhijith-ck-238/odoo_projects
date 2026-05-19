/** @odoo-module **/
import {useService} from "@web/core/utils/hooks";
const {useState, useEffect, useRef, onMounted} = owl;

import {ParentMenuConfigurationDialog, MenuCreationDialog, MenuConfigurationDialog} from "@cyllo_studio/js/studio_menu_sidebar/dialog/dialog";
//import {MenuConfigurationDialog, MenuCreationDialog, ParentMenuConfigurationDialog} from "./dialog";

import {MenuSideBar} from "@cyllo_base/js/menu_sidebar";

export class StudioMenuSideBar extends MenuSideBar {
    static template = 'cyllo_studio.StudioMenuSideBar'
    setup() {
        super.setup();
        console.log("Abhin", this)
        console.log('asdkhasdasdsad')
        var self = this
        this.dialogService = useService("dialog")
        this.menuDragRef = useRef("MenuDragRef");
        this.cySubMenuDragRef = useRef("CySubMenuDragRef");
        this.menuService = useService("menu");
        this.state = useState({
            ...this.state,
            MenuActive: false,
            MenuDraggable: false,
            CustomMenuDraggable: false,
        })
        onMounted(() => {
            console.log("mjmjmj", this)
            this.MegaMenuDrag()
            this.state.MenuDraggable = true
        })
        useEffect(() => {
            if (this.state.MenuDraggable) {
                this.MenuDrag()
                this.state.MenuDraggable = false
            }
        }, () => [this.state.MenuDraggable, this.state.CustomMenuDraggable])
        console.log("mjmjmj11", this)
    }
    createDragulaConfig(el) {
        console.log("dragulaopens")
        return dragula([el], {
            revertOnSpill: true,
            moves: (el, container, handle) => {
                console.log("lukyt")
                return handle.classList.contains("ri-drag-move-line");
            },
            accepts: (el, target, source, sibling) => {
                if (el.classList.contains('cy-SubMenuDrag') && (sibling?.classList.contains('cy-ParentMenuDrag') || !sibling)) {
                    return false;
                }
                return sibling?.classList ? sibling.classList.contains('menu-draggable') : false;
            }
        }).on('drop', async (el, target, source, sibling) => {
            const elements = source.querySelectorAll('.menu-draggable');
            console.log("123qsde",elements)
            const MenuPosition = {};
//
            elements.forEach((element, index) => {
                if (!element.classList.contains('prevent-drag') && element.hasChildNodes()) {
                    const Fields = element.attributes.menu_id ? element.attributes.menu_id.value : [null];
                    MenuPosition[index] = Fields;
                }
            });
            console.log("123qsde11",MenuPosition)
//
            await this.rpc("/cyllo_studio/move/menuitem", {
                method: 'move_menu',
                args: [],
                kwargs: {MenuPosition},
            });
              this.action.doAction("studio_reload");
//              window.location.reload()
        });
    }

    MegaMenuDrag() {
        const MenuEl = this.menuDragRef.el;
        this.createDragulaConfig(MenuEl);
    }

    MenuDrag() {
        const SubMenuEl = this.cySubMenuDragRef.el;
        this.createDragulaConfig(SubMenuEl);
    }

    ParentMenuCust(e, ParentMenu) {
         console.log("menudragbtn works")
         console.log("menudragbtn works",ParentMenu)
//         console.log("menudragbtn works",ParentMenu.id)
//         console.log("menudragbtn works",ParentMenu.appID)
         if (ParentMenu.id != ParentMenu.appID) {
            this.dialogService.add(MenuConfigurationDialog, {
            isParent: "children",
            title: 'Menu Items Configuration',
            Menu: ParentMenu,
            menuName: ParentMenu.name,
            ParentMenu: ParentMenu,
            ParentMenus: this.state.menus,
            });
         } else {
            this.dialogService.add(ParentMenuConfigurationDialog, {
                title: 'Parent Menu Items Configuration',
                menuName: ParentMenu.name,
                ParentMenus: this.state.menus,
                ParentMenu: ParentMenu,
            });
         }
    }
    studioOpenContextMenu() {
        event.preventDefault();
        var activeContextMenu = this.cyLeftSidebar.el.querySelectorAll('.studio-context-menu[style="display: flex;"]')
        activeContextMenu.forEach((menu) => {
//            If the context menu exists, set its display style to flex to show it.
            menu.style.display = 'none'
        })
        var cyLeftSidebarContextMenu = event.target.querySelector('.studio-context-menu')
        if (cyLeftSidebarContextMenu) {
            cyLeftSidebarContextMenu.style.display = 'flex';
            const hideContextMenu = () => {
                cyLeftSidebarContextMenu.style.display = 'none';
                document.removeEventListener('click', hideContextMenu);
            };
            document.addEventListener('click', hideContextMenu);
        }
    }
    itemOnClick(ParentMenu,isCreate = false) {
           console.log("123wqasddews")
//
         if(!ParentMenu && !this.menuService.getCurrentApp()?.id){
            return this.notification.add({
                    title: "Validation Error",
                    message: "Unable to complete the process.",
                    description: "You can't add menu to this model",
                    type: "notification_panel",
                    notificationType: "warning",
                });
        }
        this.dialogService.add(MenuCreationDialog, {
            isParent: "sibling",
            title: 'Menu Items Creation',
            ParentMenu: ParentMenu ? ParentMenu.id : this.menuService.getCurrentApp()?.id ?? false,
            isCreate
        });
        this.stateParentMenu = ParentMenu ? ParentMenu.id : this.menuService.getCurrentApp()?.id ?? false
    }
    ChildMenuCust(ch_menu, ParentMenu, menuChildren) {
        this.dialogService.add(MenuConfigurationDialog, {
            isParent: "sibling",
            title: 'Menu Items Configuration',
            Menu: ch_menu,
            menuName: ch_menu.name,
            ParentMenu: ParentMenu,
            ParentMenus: this.state.menus,
        });
    }
}



//createDragulaConfig(el) {
//        const sidebar = el.closest('.cy-left-sidebar');
//        let scrollInterval = null;
//        let currentMouseY = null;
//
//        // Update currentMouseY on every mousemove anywhere in the window
//        const updateMousePosition = (event) => {
//            currentMouseY = event.clientY;
//        };
//
//        const startAutoScroll = () => {
//            if (currentMouseY === null) return; // no position yet
//            const rect = sidebar.getBoundingClientRect();
//            const threshold = 40; // px near top/bottom
//            const speed = 15;
//
//            if (currentMouseY - rect.top < threshold) {
//                sidebar.scrollTop -= speed;
//            } else if (rect.bottom - currentMouseY < threshold) {
//                sidebar.scrollTop += speed;
//            }
//        };
//
//        const onMouseMove = (e) => {
//            updateMousePosition(e);
//            if (!scrollInterval) {
//                scrollInterval = setInterval(startAutoScroll, 50);
//            }
//        };
//
//        const stopAutoScroll = () => {
//            if (scrollInterval) {
//                clearInterval(scrollInterval);
//                scrollInterval = null;
//            }
//            currentMouseY = null;
//        };
//
//        const drake = dragula([el], {
//            revertOnSpill: true,
//            moves: (el, container, handle) => {
//                return handle.classList.contains("ri-drag-move-line");
//            },
//            accepts: (el, target, source, sibling) => {
//                if (el.classList.contains('cy-SubMenuDrag') &&
//                   (sibling?.classList.contains('cy-ParentMenuDrag') || !sibling)) {
//                    return false;
//                }
//                return sibling?.classList?.contains('menu-draggable') || false;
//            },
//        });
//
//        drake.on('drag', () => {
//            // Start listening globally for mousemove to track mouse Y position
//            window.addEventListener('mousemove', onMouseMove);
//        });
//
//        drake.on('drop', async (el, target, source, sibling) => {
//            window.removeEventListener('mousemove', onMouseMove);
//            stopAutoScroll();
//
//            // your existing drop logic here
//            const elements = source.querySelectorAll('.menu-draggable');
//            const MenuPosition = {};
//            elements.forEach((element, index) => {
//                if (!element.classList.contains('prevent-drag') && element.hasChildNodes()) {
//                    const Fields = element.attributes.menu_id ? element.attributes.menu_id.value : [null];
//                    MenuPosition[index] = Fields;
//                }
//            });
//
//            await this.rpc("/cyllo_studio/move/menuitem", {
//                method: 'move_menu',
//                args: [],
//                kwargs: { MenuPosition },
//            });
//
//            await this.loadMenus();
//        });
//
//        drake.on('cancel', () => {
//            window.removeEventListener('mousemove', onMouseMove);
//            stopAutoScroll();
//        });
//
//        return drake;
//    }
//    async loadMenus() {
//    // Adjust this RPC route and return data format as per your backend
//        const newMenus = await this.rpc("/cyllo_studio/get_menu_data");
//        this.state.apps = newMenus;  // assuming your template loops on this.state.apps
//    }