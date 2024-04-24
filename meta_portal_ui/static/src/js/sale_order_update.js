odoo.define('meta_portal_ui.sale_order_update', function(require) {
    'use strict';

    var publicWidget = require('web.public.widget');
    var rpc = require('web.rpc');

    publicWidget.registry.SpecificSalePortal = publicWidget.Widget.extend({
        selector: '#remark_button_div',
        events: {
            'click #give_msg': '_onClickRemarkbutton',
            'click #msg_submit': '_orderRemarkSubmit',
        },

        _onClickRemarkbutton: async function () {
            var remark_button = document.getElementById("give_msg");
            var submitButtonDiv = document.getElementById("msg_submit_button");

            submitButtonDiv.style.display = "block";
            remark_button.style.display = "none";
        },

        _orderRemarkSubmit: async function () {
            var successDiv = document.getElementById("success_div");
            var submitButtonDiv = document.getElementById("msg_submit_button");
            
            var sale_order_id = document.getElementById("sale_order_id");
            var saleId = sale_order_id.textContent;
            var msgContent = document.getElementById("msg_content");
            var order_remark = msgContent.value;

            rpc.query({
                model: 'sale.order',
                method: 'update_order_remark',
                args: [saleId, order_remark],
            }).then(function(){
                submitButtonDiv.style.display = "none";
                successDiv.style.display = "block";
            });
        },
    });
    return {
        SpecificSalePortal: publicWidget.registry.SpecificSalePortal,
    };
});