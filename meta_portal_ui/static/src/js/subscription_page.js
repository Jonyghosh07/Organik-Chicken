odoo.define('meta_portal_ui.subscription_page', function(require) {
    'use strict';

    var publicWidget = require('web.public.widget');
    var rpc = require('web.rpc');

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
            console.log("target_element -------------------> ", element);
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


    return {
        SubscriptionProductPage: publicWidget.registry.SubscriptionProductPage,
        SubscriptionModal: publicWidget.registry.SubscriptionModal,
    };
});