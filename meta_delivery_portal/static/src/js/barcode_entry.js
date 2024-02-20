odoo.define('meta_delivery_portal.item_scanner_popup', function (require) {
    "use strict";

    var publicWidget = require('web.public.widget');
    const core = require('web.core');
    const Dialog = require('web.Dialog');
    //    var CustomWidget = require('meta_delivery_portal.custom_widget'); // Import your custom widget
    const _t = core._t;
    var QWeb = core.qweb;


    publicWidget.registry.WebsitePortalDelivery = publicWidget.Widget.extend({
        selector: '.oe_portal_delivery_order_table',
        disabledInEditableMode: false,
        events: {
            'click .o_line_item': '_onClickLineItem',
        },

        /**
         * @private
         * @param {Event} ev
         */
        _onClickLineItem: async function (ev) {
            console.log("csrf_token", core.csrf_token);
            var element = $(ev.currentTarget);
            console.log("target_element ", element);
            console.log("target_element dataset lineId", parseInt(element[0].dataset.lineId));
            console.log("target_element dataset order access token ", element[0].dataset.token);
            console.log("target_element item SKU ", element.find("#item_sku").text());
            console.log("target_element line piece ", parseInt(element.find("#piece").text()));
            const lineId = parseInt(element[0].dataset.lineId);
            const order_access_token = parseInt(element[0].dataset.token);
            const item_sku = element.find("#item_sku").text();
            const target_pcs = parseInt(element.find("#piece").text());
            const target_unit_price= parseFloat(element.find("#unit_price").text().replace(/,/g, ''));

            $("#target_line_id").val(lineId);
            $("#target_item_sku").val(item_sku);
            $("#target_pcs").val(target_pcs);
            $("#target_unit_price").val(target_unit_price);

            var o_item_scanner_modal_form = $("#o_item_scanner_modal_form")

            // o_item_scanner_modal_form.append(modal_body);
            console.log("o_item_scanner_modal_form", o_item_scanner_modal_form);
            $('.oe_barcode_tablebody > tr').each(function () {
                this.remove();
            });
            o_item_scanner_modal_form.modal({
                backdrop: 'static',
                keyboard: false // This prevents closing the modal when pressing the "Esc" key
            });
            o_item_scanner_modal_form.modal('show');
            const prev_codes = await this._getAllRowsOrderLine(lineId);
            console.log("prev_codes ",typeof prev_codes , prev_codes);
           
            prev_codes.forEach(function (value) {
                const newRow = `
                    <tr>
                        <td class='d-none tbody_bracode_line_id'>${value.id}</td>                
                        <td class='tbody_item_barcode'>${value.barcode}</td>
                        <td class='tbody_item_sku d-none'>${value.item_sku}</td>
                        <td class='tbody_item_weight'>${value.weight}</td>
                        <td class='tbody_item_price'>${value.price}</td>
                        <td><a class="o_remove_scaned_row text-denger">Remove</a></td>
                    </tr>
                    `;

                $('.oe_barcode_tablebody').append(newRow);
            });

            await new Promise(r => setTimeout(() => r(), 500));
            console.log("wait 500 over");
            this._calculateTotalWeight();

            var o_barcode_input = $('.o_barcode_input');
            o_barcode_input.val('');
            o_barcode_input.focus();
        },

        _getAllRowsOrderLine: async function (order_line_id){
            return await this._rpc({
                model: "sale.order.line.barcode.line",
                method: "search_read",
                domain: [
                    ["order_line_id", "=", order_line_id],
                ],
                fields: ["id", "barcode", "item_sku" ,"weight", "price"],
            });
        },
        
        /**
         * @private
         * @param {Event} ev
         */
        _calculateTotalWeight: function (ev) {
            console.log("calculateTotalWeight called");
            let totalItemWeight = 0;
            let totalItemPcs = 0;
            let targetUnitPrice = parseFloat($("#target_unit_price").val());

            $('td.tbody_item_weight').each(function () {
                totalItemWeight += parseFloat($(this).text());
            });
            var totalPrice = totalItemWeight * targetUnitPrice;

            totalItemPcs = $('.oe_barcode_tablebody > tr').length;
            console.log("totalWeight", totalWeight);
            console.log("Table Rows", totalItemPcs);

            $('#totalPcs').text(totalItemPcs);
            $('#totalWeight').text(totalItemWeight.toFixed(3));
            $('#totalPrice').text(totalPrice.toFixed(2));
        },

    });


    publicWidget.registry.WebsitePortalDeliveryScanner = publicWidget.Widget.extend({
        selector: '.o_item_scanner_modal',
        disabledInEditableMode: false,
        events: {
            'change .o_barcode_input': '_onChangeBarcodeInput',
            'click #btn_add_row': '_onClickBtnAddRow',
            'focus .o_barcode_input': '_onFocusBarcodeInput',
            'click .o_remove_scaned_row': '_onClickRemoveRow',
            'click .oe_barcode_btn_save': '_onClickSaveButton',
            'click .oe_barcode_btn_close': '_onClickCloseButton',
        },

        init: function () {
            this._super.apply(this, arguments);
            this._onChangeBarcodeInput = _.debounce(this._onChangeBarcodeInput, 300);
            this._onClickRemoveRow = _.debounce(this._onClickRemoveRow, 400);

        },

        /**
        * @override
        */
        start: function () {
            var self = this;
            return this._super.apply(this, arguments).then(function () {
                // Init event listener
                if (!self.readonly) {
                    $(document).on('keypress', self._onKeyPress.bind(self));
                }
            });
        },
        _onKeyPress: async function (event) {
            if (event.keyCode === 13) {  // Enter
                event.preventDefault();
                await this._onChangeBarcodeInput(event);

            }
        },


        _onClickBtnAddRow: async function (ev) {
            await this._onChangeBarcodeInput(ev);
        },

        /**
         * 
         * Barcodes with embedded weight format should follow the pattern:
         * 
         * "YYCCCCCWWWWWX"
         * 
         * YY - prefix, by which the system determines that it is a weight embedded barcode. 
         *              It must be “20” or “02” for EAN 13 and “2” for UPC-A.
         * 
         * CCCCC - item SKU (note that it has to be programmed as five digits, for example "10010" or "00010").
         * WWWWW - weight (quantity) of item in grams. For example "01750" = 1.750kg
         * X - barcode checksum
         * 
         *  Samples of barcodes with embedded weight
         *  EAN 13
         * 
         * -------- If Barcode can not be scanned or damaged------
         * User Should in put the weight in Kgs
         * 
         * Nothing else will result error
         * 
         * @private
         * @param {Event} ev
         */
        _onChangeBarcodeInput: async function (ev) {
            console.log("_onChangeBarcodeInput change ", ev);
            var prefix = '';
            var barcode = '';
            var itemSku = '';
            var weightInGrams = 0;
            var weightInKgs = 0;
            var bracode_line_id = 0;
            var price = 0;
            const target_sku = $("#target_item_sku").val();
            const target_unit_price = $("#target_unit_price").val();
            const bracodeInput = $('.o_barcode_input');
            const scannedBarcode = bracodeInput.val().trim();
            console.log('scannedBarcode', scannedBarcode, 'target_unit_price',target_unit_price);

            // Checking for null or zero
            if (!scannedBarcode) {
                return;
            }

            if (scannedBarcode.length != 13) {
                itemSku = target_sku;
                weightInKgs = parseFloat(scannedBarcode);
            } else {
                barcode = scannedBarcode;
                prefix = scannedBarcode.substring(0, 2);
                itemSku = scannedBarcode.substring(2, 7);
                weightInGrams = parseInt(scannedBarcode.substring(7, 12));
                weightInKgs = (weightInGrams / 1000).toFixed(3);

            }
            price = target_unit_price * parseFloat(weightInKgs)

            if (itemSku != target_sku) {
                Dialog.alert(this, _t(`Scanned item SKU ${itemSku} does not match with order line item SKU ${target_sku}`));
                return;
            } else {
                var obj = {
                    "barcode": barcode,
                    "itemSku": itemSku,
                    "weightInKgs": weightInKgs,
                    "price": price.toFixed(2),
                }
                bracode_line_id = await this.rpcAddNewRow(obj);
                console.log("_onChangeBarcodeInput New Line ", bracode_line_id);
                obj.bracode_line_id = bracode_line_id;
                await this._createNewRow(obj);
            }
            this._calculateTotalWeight();
            bracodeInput.val(''); // Clear the input field
            bracodeInput.focus();
        },

        _createNewRow: async function (value) {
            const newRow = `
            <tr>
                <td class='d-none tbody_bracode_line_id'>${value.bracode_line_id}</td>                
                <td class='tbody_item_barcode'>${value.barcode}</td>
                <td class='tbody_item_sku d-none'>${value.itemSku}</td>
                <td class='tbody_item_weight'>${value.weightInKgs}</td>
                <td class='tbody_item_price'>${value.price}</td>
                <td><a class="o_remove_scaned_row text-denger">Remove</a></td>
            </tr>
            `;

            $('.oe_barcode_tablebody').append(newRow);

            return
        },

        rpcAddNewRow: async function (value) {
            const line_id = $("#target_line_id").val();
            const barcode_line = await this._rpc({
                model: 'sale.order.line.barcode.line',
                method: 'create',
                args: [{
                    order_line_id: line_id,
                    barcode: value.barcode,
                    item_sku: value.itemSku,
                    weight: value.weightInKgs,
                    price: value.price,
                }],
            });
            console.log("rpcAddNewRow New Line ", barcode_line);
            return barcode_line;
        },


        rpcRemoveRowDB: async function (barcode_line_id) {
            return await this._rpc({
                model: 'sale.order.line.barcode.line',
                method: 'unlink',
                args: [barcode_line_id],
            });
        },

        /**
         * @private
         * @param {Event} ev
         */
        _onClickSaveButton: async function (ev) {
            console.log("_onClickSaveButton click ", ev);
            const pcs = $('#totalPcs').text();
            const weight = $('#totalWeight').text();
            const line_id = $("#target_line_id").val();

            console.log(` _onClickSaveButton line_id ${line_id} totalPcs ${pcs} totalWeight ${weight}`);
            $('.delivery_tbody > tr').each(function () {
                if ($(this)[0].dataset.lineId === line_id){
                    console.log("rrrrrr ", $(this).find("#piece_qty >span"));
                    $(this).find("#piece_qty >span").text(pcs);
                    $(this).find("#quantity >div >span").text(weight);
                    console.log("calling blur ", $(this).find("#quantity >div >span"));
                    $(this).find("#quantity >div >span").change();

                };
            });
            $('.oe_barcode_tablebody > tr').each(function () {
                this.remove();
            });
            await new Promise(r => setTimeout(() => r(), 200));            
            $(ev.delegateTarget).modal('hide');
        },

//        _onClickCloseButton: async function (ev) {
//            const pcs = $('#totalPcs').text();
//            const weight = $('#totalWeight').text();
//            console.log(` _onClickCloseButton totalPcs ${pcs} totalWeight${weight}`);
//
//            $('.oe_barcode_tablebody > tr').each(function () {
//                this.remove();
//            });
//            await new Promise(r => setTimeout(() => r(), 200));
//            this._calculateTotalWeight();
//
//            $(ev.delegateTarget).modal('hide');
//
//        },

        _onClickCloseButton: async function (ev) {
            const pcs = $('#totalPcs').text();
            const weight = $('#totalWeight').text();
            console.log(` _onClickCloseButton totalPcs ${pcs} totalWeight${weight}`);
            $('.oe_barcode_tablebody > tr').each(function () {
                this.remove();
            });
            await new Promise(r => setTimeout(() => r(), 200));
            this._calculateTotalWeight();

            $(ev.delegateTarget).modal('hide');
        },

        /**
         * @private
         * @param {Event} ev
         */
        _onFocusBarcodeInput: function (ev) {
            console.log("Bracode Input Focused ", $(ev.currentTarget));
        },

        /**
         * @private
         * @param {Event} ev
         */
        _calculateTotalWeight: function (ev) {
            console.log("calculateTotalWeight called");
            let totalItemWeight = 0;
            let totalItemPcs = 0;
            let targetUnitPrice = parseFloat($("#target_unit_price").val());

            $('td.tbody_item_weight').each(function () {
                totalItemWeight += parseFloat($(this).text());
            });

            var totalPrice = totalItemWeight * targetUnitPrice;

            totalItemPcs = $('.oe_barcode_tablebody > tr').length;
            console.log("totalWeight", totalWeight);
            console.log("Table Rows", totalItemPcs);

            $('#totalPcs').text(totalItemPcs);
            $('#totalWeight').text(totalItemWeight.toFixed(3));
            $('#totalPrice').text(totalPrice.toFixed(2));
        },

        /**
         * @private
         * @param {Event} ev
         */
        _onClickRemoveRow: async function (ev) {
            console.log("EV", ev);
            const row = ev.target.closest('tr');
            const row_el = $(row);
            console.log("row", row);
            console.log("row elemet", row_el);
            console.log("row tbody_bracode_line_id", row_el.find('.tbody_bracode_line_id'));
            console.log("row tbody_bracode_line_id text", row_el.find('.tbody_bracode_line_id').text());
            console.log("row tbody_bracode_line_id text INT", parseInt(row_el.find('.tbody_bracode_line_id').text()));

            const barcode_line_id = parseInt(row_el.find('.tbody_bracode_line_id').text());
            await this.rpcRemoveRowDB(barcode_line_id);
            row.remove();
            this._calculateTotalWeight();
            $('.o_barcode_input').val('').focus();
        },

    });
    return {
        WebsitePortalDelivery: publicWidget.registry.WebsitePortalDelivery,
        WebsitePortalDeliveryScanner: publicWidget.registry.WebsitePortalDeliveryScanner,
    };

});
