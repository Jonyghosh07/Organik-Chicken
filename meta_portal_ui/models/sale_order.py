from odoo import api, fields, models, _
import logging

class SaleOrderInherits(models.Model):
    _inherit = "sale.order"
    
    @api.model
    def update_order_remark(self, order_id, order_remark):
        order = self.sudo().search([("id", "=", order_id)])
        if order and order_remark:
            order.partner_id.remarks = order_remark
    
    @api.model
    def sale_order_copy(self, order_id):
        order = self.sudo().search([("id", "=", order_id)])
        if order:
            order.copy()
