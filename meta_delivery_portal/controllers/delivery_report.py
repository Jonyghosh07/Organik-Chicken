from odoo.http import request
from odoo.addons.portal.controllers.portal import CustomerPortal
from odoo import fields, http, _
from datetime import date, datetime
import pytz
import logging
_logger = logging.getLogger(__name__)


class DeliveryReport(CustomerPortal):

    def _prepare_portal_layout_values(self):
        values = super(DeliveryReport, self)._prepare_portal_layout_values()
        _logger.info("_prepare_portal_layout_values.......")
        current_date = fields.datetime.now().date()

        #### Current Date using TimeZone
        today_utc = pytz.utc.localize(datetime.utcnow())
        today_tz = today_utc.astimezone(pytz.timezone(request.env.user.partner_id.sudo().tz))
        today = date(year=today_tz.year, month=today_tz.month, day=today_tz.day)
        _logger.info(f"for portal delivery man's today ----------------> {today}")

        SaleOrder = request.env['sale.order']
        domain = ['&', '&',
                  ('delivery_man', '=', request.env.user.partner_id.id),
                  ('state', 'in', ['draft', 'sale']),
                  ('delivery_date', '=', today),
                  ]

        deliveries = SaleOrder.sudo().search(domain)
        product_list = {'receipt_paid': 0, 'round_due': 0, 'final_due': 0, 'round_paid': 0}
        product_quantities = {}
        for sale in deliveries:
            for line in sale.order_line:
                product_name = line.product_id.name
                piece_qty = line.piece_qty

                if product_name in product_quantities:
                    product_quantities[product_name]['total'] = product_quantities[product_name].get('total',
                                                                                                     0) + piece_qty
                    product_quantities[product_name]['pending'] = product_quantities[product_name].get('pending', 0) + (
                        piece_qty if sale.state == 'draft' else 0)
                else:
                    product_quantities[product_name] = {'total': piece_qty,
                                                        'pending': (piece_qty if sale.state == 'draft' else 0),
                                                        'done': 0}

                if sale.state == 'sale':
                    product_quantities[product_name]['done'] = product_quantities[product_name].get('done',
                                                                                                    0) + piece_qty

            if sale.state == 'sale':
                # Sum 'final_due' and 'receipt_paid' for all sales
                product_list['final_due'] += (sale.amount_total - sale.cash_total)
                product_list['round_due'] = int(round(product_list['final_due'] / 0.5) * 0.5)
                product_list['receipt_paid'] += sale.receipt_paid
                product_list['round_paid'] = int(round(product_list['receipt_paid'] / 0.5) * 0.5)

        values.update({
            'custom_key': 'custom_value',
            'current_date': today,
            'deliveries': deliveries,
            'product_list': product_list,
            'product_quantities': product_quantities,
        })

        _logger.info(f"values---------> {values}")
        return values

