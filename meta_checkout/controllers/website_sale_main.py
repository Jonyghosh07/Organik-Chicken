from odoo import http
from odoo.addons.website_sale.controllers import main as website_sale
from odoo.http import request
from odoo import fields, http, SUPERUSER_ID, tools, _
from odoo.exceptions import ValidationError


class WebsiteSaleInherit(website_sale.WebsiteSale):
    def _get_mandatory_fields_billing(self, country_id=False):
        # req = ["name", "email", "street", "city", "country_id"]
        req = ["name", "email", "street", "country_id"]
        if country_id:
            country = request.env['res.country'].browse(country_id)
            if country.state_required:
                req += ['state_id']
            # if country.zip_required:
            #     req += ['zip']
        return req

    def _get_mandatory_fields_shipping(self, country_id=False):
        req = ["name", "street", "country_id"]
        if country_id:
            country = request.env['res.country'].browse(country_id)
            if country.state_required:
                req += ['state_id']
            # if country.zip_required:
            #     req += ['zip']
        return req



    def checkout_form_validate(self, mode, all_form_values, data):

        error = dict()
        error_message = []

        # prevent name change if invoices exist
        if data.get('partner_id'):
            partner = request.env['res.partner'].browse(int(data['partner_id']))
            if partner.exists() and not partner.sudo().can_edit_vat() and 'name' in data and (
                    data['name'] or False) != (partner.name or False):
                error['name'] = 'error'
                error_message.append(_(
                    'Changing your name is not allowed once invoices have been issued for your account. Please contact us directly for this operation.'))

        # Required fields from form
        required_fields = [f for f in (all_form_values.get('field_required') or '').split(',') if f]
        # Required fields from mandatory field function
        required_fields += mode[
                               1] == 'shipping' and self._get_mandatory_fields_shipping() or self._get_mandatory_fields_billing()
        # Check if state required
        country = request.env['res.country']
        if data.get('country_id'):
            country = country.browse(int(data.get('country_id')))
            if 'state_code' in country.get_address_fields() and country.state_ids:
                required_fields += ['state_id']

        # error message for empty required fields
        for field_name in required_fields:
            if not data.get(field_name):
                error[field_name] = 'missing'

        # email validation
        if data.get('email') and not tools.single_email_re.match(data.get('email')):
            error["email"] = 'error'
            error_message.append(_('Invalid Email! Please enter a valid email address.'))

        print(data.get('phone'))
        print(data)
        if data.get('phone') and len(data.get('phone')) < 11:
            error["phone"] = 'error'
            error_message.append(_('Phone Number Must Be 11 Digits'))

        # vat validation
        Partner = request.env['res.partner']
        if data.get("vat") and hasattr(Partner, "check_vat"):
            if data.get("country_id"):
                data["vat"] = Partner.fix_eu_vat_number(data.get("country_id"), data.get("vat"))
            partner_dummy = Partner.new({
                'vat': data['vat'],
                'country_id': (int(data['country_id'])
                               if data.get('country_id') else False),
            })
            try:
                partner_dummy.check_vat()
            except ValidationError:
                error["vat"] = 'error'

        if [err for err in error.values() if err == 'missing']:
            error_message.append(_('Some required fields are empty.'))

        return error, error_message