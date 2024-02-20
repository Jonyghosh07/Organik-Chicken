from email.policy import default
from odoo import api, fields, models, _, tools


class StockBatchDetails(models.Model):

    _inherit = "stock.lot"
    _description = "Stock Batch Fields"

    avg_wght = fields.Float(string="Average Weight per piece")
    exp_chick = fields.Integer(string="Expected No. of Chicken")
    avail_chick = fields.Integer(string="Remaining Chickens", compute="_compute_demand_qty")
    expired_chick = fields.Integer(string="Expired Chickens", default=0)
    unit_price_kg = fields.Float(string="Rate per KG")
    exp_date = fields.Date(string="Expected Date")
    sale_orders = fields.Many2many("sale.order", string="Related Sales", compute="_compute_sale_orders")
    demand_qty = fields.Integer(string="Demand Quantity", compute="_compute_demand_qty")

    def _compute_sale_orders(self):
        for item in self:
            related_sale_orders = self.env["sale.order"].search([('order_line.batch_num.id', '=', item.id)])
            item.sale_orders = [(6, 0, related_sale_orders.ids)]

    @api.onchange('unit_price_kg')
    def _onchange_unit_price_kg(self):
        for lot in self:
            if lot.product_id:
                product = lot.product_id
                product.write({
                    'lst_price': lot.unit_price_kg
                })

    @api.onchange('exp_chick', 'expired_chick')
    def _compute_demand_qty(self):
        for item in self:
            total_demand_qty = 0
            sales = self.env["sale.order"].search([])
            for sale in sales:
                for line in sale.order_line.filtered(lambda x: x.batch_num.id == item.id):
                    total_demand_qty += line.piece_qty
            item.demand_qty = total_demand_qty
            item.avail_chick = item.exp_chick - (item.expired_chick + total_demand_qty)

