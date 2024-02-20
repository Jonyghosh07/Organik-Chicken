odoo.define('meta_customer_portal.website_sale', function (require) {
'use strict';
var core = require('web.core');
var publicWidget = require('web.public.widget');

var _t = core._t;
var concurrency = require('web.concurrency');
var dp = new concurrency.DropPrevious();


publicWidget.registry.metaWebsiteCustomerPortal = publicWidget.Widget.extend({
    selector: '.oe_website_sale',
    events: {
        'change select[name="state_id"]': '_onChangeState',
        'change select[name="area_id"]': '_onChangeArea',
    },

    start: function () {
        return this._super.apply(this, arguments);
    },

    //--------------------------------------------------------------------------
    // Private
    //--------------------------------------------------------------------------
    _onChangeState: function () {

        console.log("called state_id", $("select[name='state_id']"));
        console.log("called area", $("select[name='area_id']"));
        console.log("called sub area", $("select[name='subarea_id']"));
            if (!$("select[name='state_id']").val()) {
                return;
            }
            this._rpc({
                route: "/shop/state_infos/" + $("select[name='state_id']").val(),
                params: {
                    mode: 'shipping',
                },
            }).then(function (data) {
                var selectAreas = $("select[name='area_id']");
                if (data.areas.length) {
                    selectAreas.html('');
                    selectAreas.append($("<option></option>").attr("value", -1).text("Select Areas"));

                    _.each(data.areas, function (x) {
                        var opt = $('<option>').text(x[1])
                            .attr('value', x[0])
                            .attr('data-code', x[2]);
                        selectAreas.append(opt);
                    });
                    selectAreas.parent('div').show();

                } else {
                    selectAreas.val('').parent('div').hide();
                }
            });
        },

    _onChangeArea: function () {
        if (!$("select[name='area_id']").val()) {
            return;
        }
        this._rpc({
            route: "/shop/state_area/" + $("select[name='area_id']").val(),
            params: {
                mode: 'shipping',
            },
        }).then(function (data) {
            var selectSubAreas = $("select[name='subarea_id']");
            if (data.sub_areas.length) {
                selectSubAreas.html('');
                selectSubAreas.append($("<option></option>").attr("value", -1).text("Select Sub Areas"));

                _.each(data.sub_areas, function (x) {
                    var opt = $('<option>').text(x[1])
                        .attr('value', x[0])
                        .attr('data-code', x[2]);
                    selectSubAreas.append(opt);
                });
                selectSubAreas.parent('div').show();

            } else {
                selectSubAreas.val('').parent('div').hide();
            }
        });
        },
    });

//    _onChangeSubArea: function () {
//            if (!$("select[name='subarea_id']").val()) {
//                return;
//            }
//            this._rpc({
//                route: "/shop/state_area/" + $("select[name='subarea_id']").val(),
//                params: {
//                    mode: 'shipping',
//                },
//            });
//        },
//    });
});
