/** @odoo-module */
import { ListController } from "@web/views/list/list_controller";
import { registry } from '@web/core/registry';
import { listView } from '@web/views/list/list_view';
export class saleOrderController extends ListController {
    setup() {
        super.setup();
    }
    willStart() {
        super.willStart();
        this.model.root.on('record-editable-saved', this, this.onWizardClosed);
    }
    OnApplyClick() {
        this.actionService.doAction({
            type: 'ir.actions.act_window',
            res_model: 'sale.order.filter.wizard',
            name:'Date Lot Filter',
            view_mode: 'form',
            view_type: 'form',
            views: [[false, 'form']],
            target: 'new',
            res_id: false,
        });
    }
    async onWizardClosed(payload) {
        if (payload.props.closedReason === 'apply') {
            const domain = payload.props.data.domain;
            this.model.root.query.updateDomain([domain]);
        }
    }
}
    registry.category("views").add("button_in_tree", {
    ...listView,
    Controller: saleOrderController,
    buttonTemplate: "meta_contact_sale_filter.ListView.Buttons",
});