//odoo.define('meta_batch_order.sale_update', function(require) {
//    'use strict';
//
//    var publicWidget = require('web.public.widget');
//    var core = require('web.core');
//    var rpc = require('web.rpc');
//
//    publicWidget.registry.SaleOrderCart = publicWidget.Widget.extend({
//        selector: '#cart_kg',
//        events: {
//            'blur #pc_qty': 'renderSaleOrderLines',
//            console.log("Hellllloooooooooooooooooo")
//        },
//        start: function() {
//
//              console.log("Hellllloooooooooooooooooo")
////            var self = this;
////            var saleOrderId = document.querySelector("#introduction h2 em").innerHTML;
////            rpc.query({
////                model: 'sale.order.line',
////                method: 'search_read',
////                domain: [
////                    ['order_id', '=', saleOrderId]
////                ],
////                fields: ['name', 'product_id', 'price_unit', 'product_uom_qty'],
////            }).then(function(result) {
////                self.setupSubmitButton();
////                self.renderSaleOrderLines();
////            });
////
////            return this._super.apply(this, arguments);
//        },
//    });
//});
