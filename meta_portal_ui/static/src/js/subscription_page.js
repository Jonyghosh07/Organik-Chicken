odoo.define('meta_portal_ui.subscription_page', function(require) {
    'use strict';

    var publicWidget = require('web.public.widget');
    var rpc = require('web.rpc');

    // On click Subscription Line will open a modal to edit
    publicWidget.registry.SubscriptionProductPage = publicWidget.Widget.extend({
        selector: '#subscription_div',
        events: {
            'click .subscription_tr': '_editSubscription',
        },
        /**
         * @private
         * @param {Event} ev
         */
        _editSubscription: async function (ev) {
            var element = $(ev.currentTarget);
            var subLineId = element.data('lineId');
            var product = element[0].children[1].innerText;
            var prod_piece = element[0].children[2].innerText;
            // Update product and piece in the modal
            var modalId = $("#modal_id");
            modalId.val(subLineId);
            var modalProduct = $("#modal_name");
            modalProduct.text(product);
            var modalPiece = $("#modal_piece");
            modalPiece.val(prod_piece);
            
            // Modal Opening.....
            var o_subscription_line_form = $("#o_subscription_line_form")
            o_subscription_line_form.modal({
                backdrop: 'static',
                keyboard: false // This prevents closing the modal when pressing the "Esc" key
            });
            o_subscription_line_form.modal('show');
        },
    });


    // Modal Close, Delete and Save Button
    publicWidget.registry.SubscriptionModal = publicWidget.Widget.extend({
        selector: '#o_subscription_line_form',
        events: {
            'click .oe_subscription_btn_close': '_onClickCloseButton',
            'click .oe_subscription_btn_delete': '_onClickDeleteButton',
            'click .oe_subscription_btn_save': '_onClickSaveButton',
        },

        _onClickCloseButton: async function (ev) {
            $(ev.delegateTarget).modal('hide');
        },

        _onClickDeleteButton: async function (ev) {
            var modalId = $("#modal_id");
            await this._rpc({
                model: "res.partner",
                method: "deleteSubscription",
                args: [modalId[0].value],
            }).then(function(){
                $(ev.delegateTarget).modal('hide');
                window.location.reload();
            });
        },

        _onClickSaveButton: async function (ev) {
            var modalId = $("#modal_id");
            var modalPiece = $("#modal_piece");
            await this._rpc({
                model: "res.partner",
                method: "updateSubscription",
                args: [modalId[0].value, modalPiece[0].value],
            }).then(function(){
                $(ev.delegateTarget).modal('hide');
                window.location.reload();
            });
        },
    });

    // Add Product
    publicWidget.registry.SubscriptionAdd = publicWidget.Widget.extend({
        selector: '#customize_div',
        events: {
            'click #add_prod': '_addSubscription',
            'click .oe_sub_btn_close': '_closeModal',
            'click .oe_sub_btn_save': '_saveSubscription',
        },
        /**
         * @private
         * @param {Event} ev
         */
        _addSubscription: async function (ev) {
            // Modal Opening.....
            var o_sub_add_form = $("#o_sub_add_form")
            o_sub_add_form.modal({
                backdrop: 'static',
                keyboard: false
            });
            o_sub_add_form.modal('show');

            this._selectProductOptions();
        },

        _selectProductOptions: async function() {
            // Fetch product data from the server
            const products = await this._fetchProductData();
            // Select the select element
            const selectElement = $('#select_modal_prod');
            // Clear existing options
            selectElement.empty();
            // Add default option
            selectElement.append('<option value="">Select Product</option>');
            // Populate options with product data
            products.forEach(product => {
                selectElement.append(`<option value="${product.id}">${product.name}</option>`);
            });
        },

        _fetchProductData: async function() {
            try {
                // Fetch product data from the server
                const response = await fetch('/api/get_products');
                if (!response.ok) {
                    throw new Error('Failed to fetch product data');
                }
                // Parse JSON response
                const products = await response.json();
                return products;
            } catch (error) {
                console.error('Error fetching product data:', error);
                return [];
            }
        },

        _closeModal: function(ev) {
            // Close the modal when close button is clicked
            var o_sub_add_form = $("#o_sub_add_form");
            o_sub_add_form.modal('hide');
        },
    
        _saveSubscription: async function(ev) {
            var productId = $('#select_modal_prod').val();
            var pieceValue = $('#add_piece').val();
            
            await this._rpc({
                model: "res.partner",
                method: "addSubscription",
                args: [this.getSession().user_id, productId, pieceValue],
            })

            // Close the modal
            var o_sub_add_form = $("#o_sub_add_form");
            o_sub_add_form.modal('hide');
            window.location.reload();
        }
    });


    return {
        SubscriptionProductPage: publicWidget.registry.SubscriptionProductPage,
        SubscriptionModal: publicWidget.registry.SubscriptionModal,
        SubscriptionAdd: publicWidget.registry.SubscriptionAdd,
    };
});