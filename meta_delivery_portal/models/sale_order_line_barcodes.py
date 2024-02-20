from odoo import api, fields, models, _
import logging
_logger = logging.getLogger(__name__)


class SaleOrderLineBarcodes(models.Model):
    _name = 'sale.order.line.barcode.line'
    _description = 'Sale Order Line Scanned Barcodes'

    order_line_id = fields.Many2one("Order Line")
    barcode = fields.Char("Barcode")
    item_sku = fields.Char("Item SKU")
    weight = fields.Float("Weight (Kgs)")
    price = fields.Float("Price")
    
    def _get_by_order_line_id(self, order_line_id:int):
        _logger.info(f"sale.order.line.barcode.line  order_line_id ---------->>>>>> {order_line_id}")
        return self.search(['order_line_id', '=', order_line_id]).read('id','barcode', 'item_sku', 'weight', 'price')
