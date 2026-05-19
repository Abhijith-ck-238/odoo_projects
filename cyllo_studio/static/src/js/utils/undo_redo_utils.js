/** @odoo-module **/

export function handleUndoRedo(response){
    if(response){
        let storedArray = JSON.parse(sessionStorage.getItem('UndoRedo')) || [];
        let cleanedStr = response.replace(/\s+/g, ' ').trim();
        storedArray.push(cleanedStr);
        sessionStorage.setItem('UndoRedo', JSON.stringify(storedArray));
        sessionStorage.setItem('ReDO', JSON.stringify([]));
    }
}