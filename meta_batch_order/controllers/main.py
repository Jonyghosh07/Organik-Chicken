import json
import logging
from datetime import datetime
from werkzeug.exceptions import Forbidden, NotFound
from werkzeug.urls import url_decode, url_encode, url_parse

from odoo import fields, http, SUPERUSER_ID, tools, _
from odoo.fields import Command
from odoo.http import request
from odoo.addons.base.models.ir_qweb_fields import nl2br
from odoo.addons.http_routing.models.ir_http import slug
from odoo.addons.payment import utils as payment_utils
from odoo.addons.payment.controllers import portal as payment_portal
from odoo.addons.payment.controllers.post_processing import PaymentPostProcessing
from odoo.addons.website.controllers.main import QueryURL
from odoo.addons.website.models.ir_http import sitemap_qs2dom
from odoo.exceptions import AccessError, MissingError, ValidationError
from odoo.addons.portal.controllers.portal import _build_url_w_params
from odoo.addons.website.controllers import main
from odoo.addons.website.controllers.form import WebsiteForm
from odoo.addons.sale.controllers import portal
from odoo.osv import expression
from odoo.tools import lazy
from odoo.tools.json import scriptsafe as json_scriptsafe

_logger = logging.getLogger(__name__)


class WebsiteSale(http.Controller):
    @http.route(['/shop/cart/update_json'], type='json', auth="public", methods=['POST'], website=True, csrf=False)
    def cart_update_json(
            self, product_id, line_id=None, add_qty=None, set_qty=None, display=True,
            product_custom_attribute_values=None, no_variant_attribute_values=None, **kw
    ):
        """
        This route is called :
            - When changing quantity from the cart.
            - When adding a product from the wishlist.
            - When adding a product to cart on the same page (without redirection).
        """
        order = request.website.sale_get_order(force_create=True)
        if order.state != 'draft':
            request.website.sale_reset()
            if kw.get('force_create'):
                order = request.website.sale_get_order(force_create=True)
            else:
                return {}

        if product_custom_attribute_values:
            product_custom_attribute_values = json_scriptsafe.loads(product_custom_attribute_values)

        if no_variant_attribute_values:
            no_variant_attribute_values = json_scriptsafe.loads(no_variant_attribute_values)
        values = order._cart_update(
            product_id=product_id,
            line_id=line_id,
            add_qty=add_qty,
            set_qty=set_qty,
            product_custom_attribute_values=product_custom_attribute_values,
            no_variant_attribute_values=no_variant_attribute_values,
            **kw
        )
        request.session['website_sale_cart_quantity'] = order.cart_quantity
        if not order.cart_quantity:
            request.website.sale_reset()
            return values

        values['cart_quantity'] = order.cart_quantity
        values['minor_amount'] = payment_utils.to_minor_currency_units(
            order.amount_total, order.currency_id
        ),
        values['amount'] = order.amount_total

        if not display:
            return values

        values['website_sale.cart_lines'] = request.env['ir.ui.view']._render_template(
            "website_sale.cart_lines", {
                'website_sale_order': order,
                'date': fields.Date.today(),
                'suggested_products': order._cart_accessories()
            }
        )
        values['website_sale.short_cart_summary'] = request.env['ir.ui.view']._render_template(
            "website_sale.short_cart_summary", {
                'website_sale_order': order,
            }
        )
        return values