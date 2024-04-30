odoo.define('meta_portal_ui.payment_link_button', function(require) {
    'use strict';

    var publicWidget = require('web.public.widget');
    var rpc = require('web.rpc');

    publicWidget.registry.SpecificSalePayment = publicWidget.Widget.extend({
        selector: '#div_again_order',
        events: {
            'click #payment_button': '_orderPayment',
        },

        _orderPayment: function(ev) {
            ev.preventDefault();
            var self = this;

            var sale_order_id = document.getElementById("sale_order_id");
            var saleId = sale_order_id.textContent;

            rpc.query({
                model: 'sale.order',
                method: 'sale_order_generate_link',
                args: [[saleId]],
            }).then(function(link) {
                // Redirect to the generated payment link
                window.location.href = link;
            });
        },
    });
    return {
        SpecificSalePayment: publicWidget.registry.SpecificSalePayment,
    };
});
