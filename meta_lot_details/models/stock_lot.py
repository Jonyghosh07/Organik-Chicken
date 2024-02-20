from odoo import api, fields, models, _
import logging
_logger = logging.getLogger(__name__)


class StockLotDetails(models.Model):
    _inherit = "stock.lot"

    total_sale = fields.Float(string="Total Sale", compute="_compute_total_sale")
    total_cost = fields.Float(string="Total Cost", compute="_compute_total_cost")
    
    def _compute_total_sale(self):
        for record in self:
            sale_price = 0.0
            lot_id = record.id
            lot_prod = record.product_id.id
            sales = self.env['sale.order'].sudo().search([])
            for sale in sales:
                for order_line in sale.order_line:
                    if order_line.batch_num.id == lot_id and order_line.product_id.id == lot_prod:
                        sale_price += (order_line.price_subtotal)
            if sale_price:
                record.total_sale = sale_price
            else:
                record.total_sale = 0.00

    def _compute_total_cost(self):
        for record in self:
            cost_price = 0.0
            lot_id = record.id
            lot_prod = record.product_id.id
            productions = self.env['mrp.production'].sudo().search([])
            for production in productions:
                if production.lot_producing_id.id == lot_id and production.product_id.id == lot_prod:
                    for line in production.move_raw_ids:
                        consumed = line.quantity_done
                        unit_price = line.product_id.standard_price
                        cost_price += (consumed * unit_price)
            if cost_price:
                record.total_cost = cost_price
            else:
                record.total_cost = 0.00
