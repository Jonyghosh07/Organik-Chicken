from odoo.http import request
from odoo.addons.portal.controllers import portal
from odoo import fields, http, _
from odoo.addons.portal.controllers.portal import pager as portal_pager
from odoo.osv import expression
from odoo.exceptions import AccessError, MissingError
from datetime import date, datetime
import pytz
import logging
_logger = logging.getLogger(__name__)

class DeliveryPortal(portal.CustomerPortal):

    @http.route(['/my/delivery', '/my/delivery/page/<int:page>'], type='http', auth="user", website=True)
    def portal_so_delivery_man(self, page=1, date_begin=None, date_end=None, sortby=None, filterby=None, **kw):
        if request.env.user.is_delivery_man:
            values = self._prepare_my_deliverieses_values(page, date_begin, date_end, sortby, filterby)
            pager = portal_pager(**values['pager'])

            # content according to pager and archive selected
            deliveries = values['deliveries']
            request.session['my_deliveries_history'] = deliveries.ids[:100]

            values.update({
                'pager': pager,
                'delivery': deliveries,
            })
            return request.render("meta_delivery_portal.portal_my_delivery_template", values)

    def custom_sort_key(order):
        # Combine 'customer_area' and 'customer_sub_area' for sorting
        return (order.customer_area, order.customer_sub_area)

    def _prepare_my_deliverieses_values(self, page, date_begin, date_end, sortby, filterby, domain=None, url="/my/delivery"):
        current_date = fields.datetime.now().date()

        #### Current Date using TimeZone
        today_utc = pytz.utc.localize(datetime.utcnow())
        today_tz = today_utc.astimezone(pytz.timezone(request.env.user.partner_id.sudo().tz))
        today = date(year=today_tz.year, month=today_tz.month, day=today_tz.day)
        _logger.info(f"for pending delivery man's today ----------------> {today}")

        values = self._prepare_portal_layout_values()
        Saleorder = request.env['sale.order']

        domain = expression.AND([
            domain or [],
            ['&', '&', '&', ('delivery_man', '=', request.env.user.partner_id.id), ('state', 'in', ['draft', 'sent'])
            # ['&', '&', '&', ('delivery_man', '=', request.env.user.partner_id.id), ('state', 'in', ['sent'])
             , ('delivery_date', '=', today), ('defer_status', '=', False)],
        ])

        searchbar_sortings = {
            'customer_area': {'label': _('Area'), 'order': 'customer_area'},
            'customer_sub_area': {'label': _('Sub Area'), 'order': 'customer_sub_area'},
        }
        sort_fields = ['customer_area', 'customer_sub_area']
        sort_orders = []

        # Loop through the sorting fields and get the sorting order for each field
        for field in sort_fields:
            if field in searchbar_sortings:
                sort_orders.append(searchbar_sortings[field]['order'])

        # Combine the sorting orders into a single order string, separating them with a comma
        sort_order = ",".join(sort_orders)

        values.update({
            'date': date_begin,
            'deliveries': Saleorder.sudo().search(domain, order=sort_order, limit=self._items_per_page),
            'page_name': 'delivery',
            'pager': {  # vals to define the pager.
                "url": url,
                "url_args": {'date_begin': date_begin, 'date_end': date_end, 'sortby': sortby},
                "total": Saleorder.search_count(domain),
                "page": page,
                "step": self._items_per_page,
            },
            'default_url': url,
            'searchbar_sortings': searchbar_sortings,
            'sortby': sortby,
        })
        return values

    def _delivery_get_page_view_values(self, order, access_token, **kwargs):
        values = {
            'page_name': 'delivery',
            'sale_order': order,
        }
        return self._get_page_view_values(order, access_token, values, 'my_deliveries_history', False, **kwargs)

    @http.route(['/my/delivery/<int:order_id>'], type='http', auth="user", website=True)
    def portal_delivery_page(self, order_id, report_type=None, access_token=None, message=False, download=False, **kw):
        try:
            order_sudo = self._document_check_access('sale.order', order_id, access_token=access_token)
        except (AccessError, MissingError):
            return request.redirect('/my')

        if report_type in ('html', 'pdf', 'text'):
            return self._show_report(model=order_sudo, report_type=report_type,
                                     report_ref='sale.action_report_saleorder', download=download)

        backend_url = f'/web#model={order_sudo._name}' \
                      f'&id={order_sudo.id}' \
                      f'&action={order_sudo._get_portal_return_action().id}' \
                      f'&view_type=form'
        values = {
            'sale_order': order_sudo,
            'message': message,
            'report_type': 'html',
            'backend_url': backend_url,
            'res_company': order_sudo.company_id,  # Used to display correct company logo
        }

        if order_sudo.state in ('draft', 'sent', 'cancel'):
        # if order_sudo.state in ('sent', 'cancel'):
            history_session_key = 'my_quotations_history'
        else:
            history_session_key = 'my_orders_history'

        values = self._get_page_view_values(
            order_sudo, access_token, values, history_session_key, False)
        print("Values", values)

        values = self._delivery_get_page_view_values(order_sudo, access_token, **kw)

        return request.render('meta_delivery_portal.my_oder_portal_template', values)
