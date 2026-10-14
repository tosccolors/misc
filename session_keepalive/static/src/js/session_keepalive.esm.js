/** @odoo-module **/
import { registry } from "@web/core/registry";

export const keepaliveService = {
    async: true,
    dependencies: ["rpc"],
    async start(env, {rpc}) {
        const keepalive = await rpc('/session_keepalive');
        window.setInterval(this.keepalive, keepalive.timeout * 1000 * 3600, rpc, this.handle_session_timeout);
    },
    async keepalive(rpc, error_handler) {
        try {
            const keepalive = await rpc('/session_keepalive');
            if (typeof keepalive.timeout !== 'number') {
                error_handler()
            }
        } catch {
            error_handler()
        }
    },
    handle_session_timeout() {
        // TODO: handle hard session timeout
    },
}
registry.category("services").add("session_keepalive", keepaliveService);
