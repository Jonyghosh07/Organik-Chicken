from odoo.http import request
from odoo.addons.portal.controllers import portal
from odoo import fields, http, tools, _, SUPERUSER_ID
from odoo.addons.portal.controllers.portal import pager as portal_pager
from odoo.osv import expression
from odoo.exceptions import AccessError, MissingError
from datetime import date, datetime
import pytz
import logging
_logger = logging.getLogger(__name__)


class DoneDeliveryPortal(portal.CustomerPortal):

    @http.route(['/done/delivery', '/done/delivery/page/<int:page>'], type='http', auth="user", website=True)
    def portal_done_delivery_man(self, page=1, date_begin=None, date_end=None, sortby=None, filterby=None, **kw):
        if request.env.user.is_delivery_man:
            values = self._prepare_done_deliveries_values(page, date_begin, date_end, sortby, filterby)
            pager = portal_pager(**values['pager'])

            # content according to pager and archive selected
            deliveries = values['deliveries']
            request.session['my_deliveries_history'] = deliveries.ids[:100]

            values.update({
                'pager': pager,
                'done_delivery': deliveries,
            })
            return request.render("meta_delivery_portal.portal_done_delivery_template", values)

    def _prepare_done_deliveries_values(self, page, date_begin, date_end, sortby, filterby, domain=None, url="/done/delivery"):
        current_date = fields.datetime.now().date()

        #### Current Date using TimeZone
        today_utc = pytz.utc.localize(datetime.utcnow())
        today_tz = today_utc.astimezone(pytz.timezone(request.env.user.partner_id.sudo().tz))
        today = date(year=today_tz.year, month=today_tz.month, day=today_tz.day)
        _logger.info(f"for done delivery delivery man's today ----------------> {today}")

        values = self._prepare_portal_layout_values()
        Saleorder = request.env['sale.order']

        # domain = expression.AND([
        #     domain or [],
        #     ['|', '&', ('state', '=', 'draft'), ('defer_status', '!=', False), '&',
        #         ('delivery_man', '=', request.env.user.partner_id.id), ('state', 'in', ['sale']),
        #         ('delivery_date', '=', today)],
        # ])
        domain = expression.AND([
            [('delivery_man', '=', request.env.user.partner_id.id), ('delivery_date', '=', today)],
            ['|',
                ('state', 'in', ['sale']),
                '&', ('state', '=', 'draft'), ('defer_status', '!=', False)
            ]
        ])

        searchbar_sortings = {
            'date': {'label': _('Date'), 'order': 'date_order desc'},
            'name': {'label': _('Reference'), 'order': 'name desc'},
            'state': {'label': _('Status'), 'order': 'state'},
        }
        # default sort by order
        if not sortby:
            sortby = 'date'
        order = searchbar_sortings[sortby]['order']

        values.update({
            'date': date_begin,
            'deliveries': Saleorder.sudo().search(domain, order=order, limit=self._items_per_page),
            'page_name': 'done_delivery',
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
            'filterby': filterby,
        })
        return values

    def _done_delivery_get_page_view_values(self, order, access_token, **kwargs):
        values = {
            'page_name': 'done_delivery',
            'sale_order': order,
        }
        return self._get_page_view_values(order, access_token, values, 'my_deliveries_history', False, **kwargs)

    @http.route(['/done/delivery/<int:order_id>'], type='http', auth="user", website=True)
    def portal_done_delivery_page(self, order_id, report_type=None, access_token=None, message=False, download=False, **kw):
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
            history_session_key = 'my_quotations_history'
        else:
            history_session_key = 'my_orders_history'

        values = self._get_page_view_values(
            order_sudo, access_token, values, history_session_key, False)
        print("Values", values)

        values = self._done_delivery_get_page_view_values(order_sudo, access_token, **kw)

        return request.render('meta_delivery_portal.done_oder_portal_template', values)