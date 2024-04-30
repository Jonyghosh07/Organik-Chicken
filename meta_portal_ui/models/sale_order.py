from odoo import api, fields, models, _
import logging
from odoo.addons.payment import utils as payment_utils
from werkzeug import urls

class SaleOrderInherits(models.Model):
    _inherit = "sale.order"
    
    @api.model
    def update_order_remark(self, order_id, order_remark):
        order = self.sudo().search([("id", "=", order_id)])
        if order and order_remark:
            order.custom_remarks = order_remark
    
    @api.model
    def sale_order_copy(self, order_id):
        order = self.sudo().search([("id", "=", order_id)])
        if order:
            order.copy()
    
    @api.model
    def sale_order_generate_link(self, sale_id):
        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        order = self.sudo().search([("id", "=", sale_id)])
        url_params = {
            'reference': order.name,
            'amount': order.amount_total,
            'access_token': payment_utils.generate_access_token(
                                order.partner_id.id, order.amount_total, order.currency_id.id
                            ),
        }
        link = f'{base_url}/payment/pay?{urls.url_encode(url_params)}'
        return link
