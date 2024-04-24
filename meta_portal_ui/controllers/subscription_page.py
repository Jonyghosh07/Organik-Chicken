from odoo.http import request
from odoo.addons.portal.controllers import portal
from odoo import fields, http, tools, _, SUPERUSER_ID
from odoo.addons.portal.controllers.portal import pager as portal_pager
import logging
_logger = logging.getLogger(__name__)


class CustomerSubscriptionPortal(portal.CustomerPortal):
    
    @http.route(['/customer/subscription'], type='http', auth="user", website=True)
    def portal_customer_subscription(self, **kw):
        user = request.env.user
        values = self._prepare_subscription_values(user)
        return request.render("meta_portal_ui.portal_customer_subscription_template", {'subscription_values': values})
    
    
    def _prepare_subscription_values(self, user):
        if user:
            partner = request.env['res.partner'].sudo().search([('id', '=', user.partner_id.id)])
            subscription_values = []
            if partner.is_subscriber and partner.subscription_line:
                for line in partner.subscription_line:
                    id = line.id
                    product = line.product_id.name
                    piece = line.piece_qty
                    subscription_values.append({
                        'id': id,
                        'product': product,
                        'piece': piece,
                    })        
        return subscription_values