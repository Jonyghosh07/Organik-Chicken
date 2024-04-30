odoo.define('meta_portal_ui.sale_order_copy', function(require) {
    'use strict';

    var publicWidget = require('web.public.widget');
    var rpc = require('web.rpc');

    publicWidget.registry.SpecificSaleCopy = publicWidget.Widget.extend({
        selector: '#div_again_order',
        events: {
            'click #order_again': '_orderCopySubmit',
        },

        _orderCopySubmit: async function () {
            var sale_order_id = document.getElementById("sale_order_id");
            var saleId = sale_order_id.textContent;
            var order_button = document.getElementById("order_again");
            var successDiv = document.getElementById("copy_success");
            rpc.query({
                model: 'sale.order',
                method: 'sale_order_copy',
                args: [saleId],
            }).then(function(){
                order_button.style.display = "none";
                successDiv.style.display = "block";
            });
        },
    });
    return {
        SpecificSaleCopy: publicWidget.registry.SpecificSaleCopy,
    };
});