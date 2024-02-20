# -*- coding: utf-8 -*-
from datetime import datetime

from odoo import models, fields, _, api


class CourierSaleOrder(models.Model):
    _inherit = 'sale.order'
    _description = 'Courier Sale Order'

    cancel_date = fields.Datetime(String="Cancel Date")
    shipping_method = fields.Many2one('delivery.carrier', string="Shipping Method")
    payment_method = fields.Char('Payment Method', compute='_compute_payment_method')
    delivery_done = fields.Boolean('Delivered')
    delivery_done_date = fields.Date('Delivered Time')

    @api.onchange("delivery_done")
    def get_delivery_done_date(self):

        print("cvdsd")
        print("cjheck", self.delivery_done)
        if self.delivery_done == True:
            self.delivery_done_date = fields.Datetime.now()
        else:
            self.delivery_done_date = False

    def _compute_payment_method(self):
        for order in self:
            payment_tra = order.env['payment.transaction'].search(
                [('sale_order_ids', 'in', order.id)], limit=1)
            if payment_tra:
                order.payment_method = payment_tra.provider_id.name
            else:
                order.payment_method = False

    def action_cancel(self):
        self.cancel_date = datetime.today()
        res = super(CourierSaleOrder, self).action_cancel()
        return res
