import logging

from odoo import http
from odoo.exceptions import AccessError
from odoo.http import request
_logger = logging.getLogger(__name__)


class Tracking(http.Controller):

    @http.route('/track_order', type="http", auth="public", website=True)
    def track_order(self, **kw):
        return http.request.render('meta_track_order.get_order_id', {})

    @http.route('/search_order_id', type="http", auth="public", website=True)
    def search_order_id(self, **kw):
        customer_sale_id = []
        is_tracking_order = ''
        if kw:
            q = kw['order_id']
            customer_phone = request.env['res.partner'].sudo().search([('phone', '=', q)])
            customer_email = request.env['res.partner'].sudo().search([('email', '=', q)])
            print("customer_email", customer_email)
            if len(customer_phone) > 0:
                customer_sale_id = request.env['sale.order'].sudo().search([('partner_id', '=', customer_phone[0].id)],
                                                                           limit=10)
            if len(customer_email) > 0:
                customer_sale_id = request.env['sale.order'].sudo().search([('partner_id', '=', customer_email[0].id)],
                                                                           limit=10)

            print("customer_sale_id", customer_sale_id)
            try:
                if len(customer_phone) < 1 and len(customer_email) < 1:
                    if q[0] == 's':
                        a = list(q)
                        a[0] = "S"
                        q = "".join(a)
                    customer_sale_id = http.request.env['sale.order'].sudo().search([('name', '=', q)], limit=1)
                current_user = request.env['res.users'].browse(request.env.uid)

                if len(customer_sale_id) < 1:
                    is_tracking_order = 'no_order'
                    _logger.warning('check is_tracking_order: %s', is_tracking_order)
                    return http.request.render('meta_track_order.tracking_info',
                                               {'is_tracking_order': is_tracking_order})
                elif current_user.partner_id.id == customer_sale_id[0].partner_id.id and current_user.partner_id.id != 4:
                    is_tracking_order = 'user'
                    print("customer_sale_id", customer_sale_id)
                    _logger.warning('check is_tracking_order: %s', is_tracking_order)
                    return http.request.render('meta_track_order.tracking_info',
                                               {'is_tracking_order': is_tracking_order, 'sale_id': customer_sale_id})
                else:
                    is_tracking_order = 'other_order'
                    _logger.warning('check is_tracking_order:ot %s', is_tracking_order)
                    return http.request.render('meta_track_order.tracking_info',
                                               {'is_tracking_order': is_tracking_order, 'sale_id': customer_sale_id})



            except:
                if AccessError:
                    q = kw['order_id']
                    customer_phone = request.env['res.partner'].sudo().search([('phone', '=', q)])
                    customer_email = request.env['res.partner'].sudo().search([('email', '=', q)])
                    if len(customer_phone) > 0:
                        customer_sale_id = request.env['sale.order'].sudo().search(
                            [('partner_id', '=', customer_phone.id)], limit=10)
                    elif len(customer_email) > 0:
                        customer_sale_id = request.env['sale.order'].sudo().search(
                            [('partner_id', '=', customer_email.id)], limit=10)
                        if not customer_sale_id:
                            is_tracking_order = 'no_order'
                    if len(customer_phone) < 1 and len(customer_email) < 1:
                        if q[0] == 's':
                            a = list(q)
                            a[0] = "S"
                            q = "".join(a)
                    sale_id = request.env['sale.order'].search([('name', '=', q)], limit=1)
                    is_tracking_order = 'other_order'
                    if not sale_id:
                        is_tracking_order = 'no_order'
                    _logger.warning('check is_tracking_order:except %s', is_tracking_order)
                    return http.request.render('meta_track_order.tracking_info',
                                               {'is_tracking_order': is_tracking_order,
                                                'sale_id': sale_id
                                                })
