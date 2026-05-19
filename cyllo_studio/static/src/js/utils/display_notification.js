/** @odoo-module **/

export function DisplayNotification(env, options = {}) {
    const defaultOptions = {
        message: 'Select a field',
        type: 'warning',
        sticky: false
    };

    // Merge default options with provided options
    const finalOptions = { ...defaultOptions, ...options };

    env.action.doAction({
        'type': 'ir.actions.client',
        'tag': 'display_notification',
        'params': finalOptions
    });
}