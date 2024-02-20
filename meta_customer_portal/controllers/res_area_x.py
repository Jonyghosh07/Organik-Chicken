from odoo import fields, http, SUPERUSER_ID, tools, _
from odoo.http import request
from werkzeug.exceptions import Forbidden
from odoo.addons.website_sale.controllers.main import WebsiteSale
from odoo.exceptions import ValidationError
import logging

logger = logging.getLogger(__name__)


class WebsiteSaleExtended(WebsiteSale):
    WRITABLE_PARTNER_FIELDS = WebsiteSale.WRITABLE_PARTNER_FIELDS + [
        "area_id",
        "sub_area_id",
        "whatsapp_num",
    ]

    @http.route(['/shop/state_infos/<model("res.country.state"):state>'], type="json", auth="public", methods=["POST"], website=True)
    def state_infos(self, state, mode, **kw):
        return dict(
            areas=[(st.id, st.name) for st in state.get_website_sale_ares()],
        )

    @http.route(['/shop/state_area/<model("res.country.state"):state>'], type="json", auth="public", methods=["POST"], website=True)
    def area_infos(self, state, mode, **kw):
        return dict(
            sub_areas=[(a.id, a.name) for a in state.get_website_sale_sub_areas()],
        )

    def checkout_check_address(self, order):
        billing_fields_required = self._get_mandatory_fields_billing(order.partner_id.country_id.id)
        if not all(order.partner_id.read(billing_fields_required)[0].values()):
            return request.redirect("/shop/address?partner_id=%d" % order.partner_id.id)

        shipping_fields_required = self._get_mandatory_fields_shipping(order.partner_shipping_id.country_id.id)
        if not all(order.partner_shipping_id.read(shipping_fields_required)[0].values()):
            return request.redirect("/shop/address?partner_id=%d" % order.partner_shipping_id.id)

    @http.route(["/shop/address"], type="http", methods=["GET", "POST"], auth="public", website=True, sitemap=False)
    def address(self, **kw):
        Partner = request.env["res.partner"].with_context(show_address=1).sudo()
        order = request.website.sale_get_order()

        redirection = self.checkout_redirection(order)
        if redirection:
            return redirection

        mode = (False, False)
        can_edit_vat = False
        def_country_id = order.partner_id.country_id
        def_state_id = order.partner_id.state_id
        values, errors = {}, {}

        partner_id = int(kw.get("partner_id", -1))

        # IF PUBLIC ORDER
        if order.partner_id.id == request.website.user_id.sudo().partner_id.id:
            mode = ('new', 'billing')
            can_edit_vat = True
            country_code = request.session['geoip'].get('country_code')
            if country_code:
                def_country_id = request.env['res.country'].search([('code', '=', country_code)], limit=1)
            else:
                def_country_id = request.website.user_id.sudo().country_id
                def_state_id = request.website.user_id.sudo().state_id
        # IF ORDER LINKED TO A PARTNER
        else:
            if partner_id > 0:
                if partner_id == order.partner_id.id:
                    mode = ("edit", "billing")
                    can_edit_vat = order.partner_id.can_edit_vat()
                else:
                    shippings = Partner.search([("id", "child_of", order.partner_id.commercial_partner_id.ids)])
                    if order.partner_id.commercial_partner_id.id == partner_id:
                        mode = ("new", "shipping")
                        partner_id = -1
                    elif partner_id in shippings.mapped("id"):
                        mode = ("edit", "shipping")
                    else:
                        return Forbidden()
                if mode and partner_id != -1:
                    values = Partner.browse(partner_id)
            elif partner_id == -1:
                mode = ("new", "shipping")
            else:  # no mode - refresh without post?
                return request.redirect("/shop/checkout")

        # IF POSTED
        if "submitted" in kw and request.httprequest.method == "POST":
            pre_values = self.values_preprocess(kw)
            errors, error_msg = self.checkout_form_validate(mode, kw, pre_values)
            post, errors, error_msg = self.values_postprocess(order, mode, pre_values, errors, error_msg)

            post["area_id"] = pre_values.get("area_id") or False
            post["sub_area_id"] = int(pre_values.get("subarea_id")) or False
            post["whatsapp_num"] = pre_values.get("whatsapp") or False
            logger.info("Post Values =====> %s" % post)

            if errors:
                errors["error_message"] = error_msg
                values = kw
            else:
                partner_id = self._checkout_form_save(mode, post, kw)
                # We need to validate _checkout_form_save return, because when partner_id not in shippings
                # it returns Forbidden() instead the partner_id
                if isinstance(partner_id, Forbidden):
                    return partner_id
                fpos_before = order.fiscal_position_id
                if mode[1] == "billing":
                    order.partner_id = partner_id
                    # This is the *only* thing that the front end user will see/edit anyway when choosing billing address
                    order.partner_invoice_id = partner_id
                    if not kw.get("use_same"):
                        kw["callback"] = kw.get("callback") or (
                            not order.only_services and (mode[0] == "edit" and "/shop/checkout" or "/shop/address")
                        )
                    # We need to update the pricelist(by the one selected by the customer), because onchange_partner reset it
                    # We only need to update the pricelist when it is not redirected to /confirm_order
                    if kw.get("callback", False) != "/shop/confirm_order":
                        request.website.sale_get_order(update_pricelist=True)
                elif mode[1] == "shipping":
                    order.partner_shipping_id = partner_id

                if order.fiscal_position_id != fpos_before:
                    order._recompute_taxes()

                # TDE FIXME: don't ever do this
                # -> TDE: you are the guy that did what we should never do in commit e6f038a
                order.message_partner_ids = [(4, partner_id), (3, request.website.partner_id.id)]
                if not errors:
                    return request.redirect(kw.get('callback') or '/shop/confirm_order')

        country = 'country_id' in values and values['country_id'] != '' and request.env['res.country'].browse(
            int(values['country_id']))
        states = 'state_id' in values and values['state_id'] != '' and request.env['res.country.state'].browse(
            int(values['state_id']))
        country = country and country.exists() or def_country_id
        states = states and states.exists() or def_state_id

        render_values = {
            'website_sale_order': order,
            'partner_id': partner_id,
            'mode': mode,
            'checkout': values,
            'can_edit_vat': can_edit_vat,
            'country': country,
            'countries': country.get_website_sale_countries(mode=mode[1]),
            'state': states,
            'states': country.get_website_sale_states(mode=mode[1]),
            'areas': states.get_website_sale_ares(),
            'sub_areas': states.get_website_sale_sub_areas(),
            'error': errors,
            'callback': kw.get('callback'),
            'only_services': order and order.only_services,
        }
        render_values.update(self._get_country_related_render_values(kw, render_values))
        return request.render("website_sale.address", render_values)


class CustomWebsiteSale(WebsiteSale):
    def _get_mandatory_fields_shipping(self, country_id=False):
        req = ["name", "street", "country_id"]
        if country_id:
            country = request.env["res.country"].browse(country_id)
            if country.state_required:
                req += ["state_id"]
        return req

    def _get_mandatory_fields_billing(self, country_id=False):
        req = ["name", "email", "street", "country_id"]
        if country_id:
            country = request.env["res.country"].browse(country_id)
            if country.state_required:
                req += ["state_id"]
        return req

    def checkout_form_validate(self, mode, all_form_values, data):
        error = dict()
        error_message = []

        # prevent name change if invoices exist
        if data.get('partner_id'):
            partner = request.env['res.partner'].browse(int(data['partner_id']))
            if partner.exists() and partner.sudo().name and not partner.sudo().can_edit_vat() and 'name' in data and (data['name'] or False) != (partner.sudo().name or False):
                error['name'] = 'error'
                error_message.append(_('Changing your name is not allowed once invoices have been issued for your account. Please contact us directly for this operation.'))

        # Required fields from form
        required_fields = [f for f in (all_form_values.get('field_required') or '').split(',') if f]

        # Required fields from mandatory field function
        country_id = int(data.get('country_id', False))
        required_fields += mode[1] == 'shipping' and self._get_mandatory_fields_shipping(country_id) or self._get_mandatory_fields_billing(country_id)

        # error message for empty required fields
        for field_name in required_fields:
            val = data.get(field_name)
            if isinstance(val, str):
                val = val.strip()
            if not val:
                error[field_name] = 'missing'

        # vat validation
        Partner = request.env['res.partner']
        if data.get("vat") and hasattr(Partner, "check_vat"):
            if country_id:
                data["vat"] = Partner.fix_eu_vat_number(country_id, data.get("vat"))
            partner_dummy = Partner.new(self._get_vat_validation_fields(data))
            try:
                partner_dummy.check_vat()
            except ValidationError as exception:
                error["vat"] = 'error'
                error_message.append(exception.args[0])

        if [err for err in error.values() if err == 'missing']:
            error_message.append(_('Some required fields are empty.'))

        return error, error_message
