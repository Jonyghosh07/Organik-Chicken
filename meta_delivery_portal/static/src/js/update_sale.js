odoo.define('meta_delivery_portal.update_sale', function(require) {
    'use strict';

    var publicWidget = require('web.public.widget');
    var core = require('web.core');
    var rpc = require('web.rpc');

    publicWidget.registry.SaleOrderPortal = publicWidget.Widget.extend({
        selector: '#sale_order_portal_custom',
        events: {
            'blur #quantity div span': 'renderSaleOrderLines',
            'blur #unit_price div': 'renderSaleOrderLines',
            'change #quantity div span': 'updateSaleOrderRecord',
        },
        start: function() {
            var self = this;
            var saleOrderId = document.querySelector("#introduction h2 em").innerHTML;
            var sale_order_id = document.getElementById("sale_order_id");
            var saleId = sale_order_id.textContent;
            rpc.query({
                model: 'sale.order.line',
                method: 'search_read',
                domain: [
                    ['order_id', '=', saleOrderId]
                ],
                fields: ['name', 'product_id', 'price_unit', 'product_uom_qty'],
            }).then(function(result) {
                self.setupDoneButton(saleId);
                self.setupCancelButton(saleId);
                self.renderSaleOrderLines();
            });

            return this._super.apply(this, arguments);
        },



        ///////////////////////////////////////////////////////
        renderSaleOrderLines: function(saleOrderLines) {
            const selectElement = document.getElementById("options_list");
            const amountInput = document.getElementById("amount_rcvd");
            const doneButtonDiv = document.getElementById("done_button");
            console.log("done Button ------------> ", doneButtonDiv)
            const resultElement = document.getElementById("result");
            //Amount Received
            var $amountReceivedInput = this.$('#amount_rcvd');

            // Function to update amount and result
            function updateAmountAndResult() {
                if (selectElement.value === "bkash" || selectElement.value === "bank") {
                    amountInput.value = "0.00";
                    amountInput.readOnly = true;
                    doneButtonDiv.style.display = "block";
                } else {
                    amountInput.readOnly = false;
                    $amountReceivedInput.on('input', function() {
                        // Value of Amount Received
                        var amountReceived = parseFloat($(this).val());
                        doneButtonDiv.style.display = "block";
                        
                        if (amountReceived > 100) {
                            // Calculation
                            var result = numericValue - amountReceived;
                            // Call Due
                            var $resultElement = $('#result');
                            // Replace Due Value with Updated Value
                            $resultElement.text(result.toFixed(2));
                        } else{
                            doneButtonDiv.style.display = "none";
                            // Calculation
                            var result = numericValue - amountReceived;
                            // Call Due
                            var $resultElement = $('#result');
                            // Replace Due Value with Updated Value
                            $resultElement.text(result.toFixed(2));
                        }
                    });
                }

                // Calculation
                var value = document.getElementById('total_payable').querySelector('span').textContent.trim();
                var numericValue = parseFloat(value.replace(/[^0-9.-]+/g, ''));
                var amountReceived = parseFloat(amountInput.value);
                var result = numericValue - amountReceived;
                resultElement.textContent = result.toFixed(2);
            }

            // Initial update
            updateAmountAndResult();

            // Event listener for changes in payment option
            selectElement.addEventListener("change", updateAmountAndResult);
        },

        //Cancel Button
        setupCancelButton: function(saleId) {
            var self = this;
            var $cancelButton = this.$('#cancelButton');
            $cancelButton.on('click', function(ev) {
                console.log("cancel clicked------->")
                ev.preventDefault();
                var o_warning_modal_form = $("#o_warning_modal_form")
                o_warning_modal_form.modal({
                    backdrop: 'static',
                    keyboard: false // This prevents closing the modal when pressing the "Esc" key
                });
                o_warning_modal_form.modal('show');
                $("#o_warning_modal_form .oe_warning_btn_close").on('click', function () {
                    // Handle the "Cancel" button click here
                    $("#o_warning_modal_form").modal('hide');
                });

                $("#o_warning_modal_form .oe_warning_btn_save").on('click', function () {
                    var status = $("#delivery_status_select").val();
                    var date = $("#date_delivery").val();
                    console.log("status -------->", status)
                    console.log("date -------->", date)
                    rpc.query({
                        model: 'sale.order',
                        method: 'update_delivery_status',
                        args: [saleId, status, date],
                    }).then(function(result){
                        $("#o_warning_modal_form").modal('hide');
                        window.location = '/my/delivery';
                    });
                });

            });
        },

        //Done Button
        setupDoneButton: async function (saleId) {
            var self = this;
            var $doneButton = this.$('#doneButton');
            await $doneButton.on('click', async function (ev) {
                console.log("Done Button clicked")
                ev.preventDefault();
                    self.confirmSaleOrderRecord(saleId);
                    window.location = '/my/delivery';
                });
        },

        //Confirm Sale Order
        confirmSaleOrderRecord: async function (saleId) {
            console.log("confirmSaleOrderRecord Function Called")
            var self = this;
            var fieldsToUpdate = [];
            // Amount received
            var amountReceived = document.getElementById('amount_rcvd');
            var Received = amountReceived.value;

            // Map URL
            var urlReceived = document.getElementById('o_url_input');
            var map_url = urlReceived.value;
            console.log("map_url -----------------------> ", map_url)

            // Payment option for Journal ID
            var paymentOptionSelect = document.querySelector("#payment_option select");
            var selectedPaymentOption = paymentOptionSelect.value;

            // List of fields passing
            // Check if map_url has a value
            if (map_url) {
                // If map_url has a value, include it in fieldsToUpdate
                fieldsToUpdate.push({
                    received: Received,
                    map_url: map_url,
                    payment_option: selectedPaymentOption,
                });
                console.log("fieldsToUpdate -----------------------> ", fieldsToUpdate)
            } else {
                // If map_url does not have a value, exclude it from fieldsToUpdate
                fieldsToUpdate.push({
                    received: Received,
                    payment_option: selectedPaymentOption,
                });
            }

            await rpc.query({
                model: 'sale.order',
                method: 'update_order_status',
                args: [saleId, fieldsToUpdate],
            });
            return;
        },
        //Update Sale Order Record on Odoo
        updateSaleOrderRecord: async function() {
            console.log("updateSaleOrderRecord change ");

            var self = this;
            const saleOrderId = document.querySelector("#introduction h2 em").innerHTML;
            var recordIds = [];
            var linesToUpdate = [];

            const paymentOptionSelect = document.querySelector("#payment_option select");
            const selectedPaymentOption = paymentOptionSelect.value;

            var $lineRows = this.$('.delivery_tbody tr:not(.is-subtotal)');
            console.log("updateSaleOrderRecord $lineRows",$lineRows);

            $lineRows.each(function() {
                const $lineRow = $(this);
                const lineId = parseInt($lineRow.find('#sale_order_line_id').text().replace(/,/g, ''));
                console.log("updateSaleOrderRecord lineId",lineId);
                
                const piece_qty = parseInt($lineRow.find('#piece_qty span').text());
                const quantity = parseFloat($lineRow.find('#quantity div span').text().replace(/,/g, ''));
                const unitPrice = parseFloat($lineRow.find('#unit_price div').text().replace(/,/g, ''));
                const amount = parseFloat($lineRow.find('.oe_order_line_price_subtotal span').text().replace(/,/g, ''));

                console.log("piece_qty:", piece_qty, 'quantity:', quantity, 'unitPrice:', unitPrice);
                recordIds.push(lineId);
                linesToUpdate.push({
                    id: lineId,
                    piece_qty:piece_qty,
                    product_uom_qty: quantity,
                    price_unit: unitPrice,
                    payment_option: selectedPaymentOption,
                });
            });
            console.log("saleOrderId",saleOrderId, "linesToUpdate", linesToUpdate),
            await rpc.query({
                model: 'sale.order',
                method: 'update_order_lines',
                args: [saleOrderId, linesToUpdate],
            });
            await new Promise(r => setTimeout(() => r(), 300));

            window.location.reload();
            return;
        },
    });

    return {
        SaleOrderPortal: publicWidget.registry.SaleOrderPortal,
    };
});