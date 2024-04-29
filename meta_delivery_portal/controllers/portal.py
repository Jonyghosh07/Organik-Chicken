from odoo.http import request
from odoo.addons.portal.controllers.portal import CustomerPortal, pager as portal_pager
from odoo import fields, http, tools, _, SUPERUSER_ID
from datetime import date, datetime
import pytz
from odoo.osv import expression
import logging
_logger = logging.getLogger(__name__)


class MyDeliveryPortal(CustomerPortal):

    def _prepare_home_portal_values(self, counters):
        current_date = fields.datetime.now().date()

        #### Current Date using TimeZone
        today_utc = pytz.utc.localize(datetime.utcnow())
        today_tz = today_utc.astimezone(pytz.timezone(request.env.user.partner_id.sudo().tz))
        today = date(year=today_tz.year, month=today_tz.month, day=today_tz.day)
        _logger.info(f"_prepare_home_portal_values delivery man's today ----------------> {today}")

        values = super()._prepare_home_portal_values(counters)
        if 'delivery_count' in counters:
            values['delivery_count'] = request.env['sale.order'].sudo().search_count(
                ['&', '&', '&', ('delivery_man', '=', request.env.user.partner_id.id), ('state', 'in', ['draft', 'sent']),
                # ['&', '&', '&', ('delivery_man', '=', request.env.user.partner_id.id), ('state', 'in', ['sent']),
                ('delivery_date', '=', today), ('defer_status', '=', False)]) \
                if request.env['sale.order'].sudo().check_access_rights('read', raise_exception=False) else 0

        if 'done_delivery_count' in counters:
            domain = expression.AND([
                    [('delivery_man', '=', request.env.user.partner_id.id), ('delivery_date', '=', today)],
                    ['|',
                        ('state', 'in', ['sale']),
                        '&', ('state', '=', 'draft'), ('defer_status', '!=', False)
                        # '&', ('state', '=', 'sent'), ('defer_status', '!=', False)
                    ]
                ])
            values['done_delivery_count'] = request.env['sale.order'].sudo().search_count(domain) \
                if request.env['sale.order'].sudo().check_access_rights('read', raise_exception=False) else 0

        return values