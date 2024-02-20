from odoo import models, _, fields, api 

class SaleReport(models.Model):
    _inherit= 'sale.report'

    qty_piece = fields.Integer(string="QTY in Piece", readonly=True)
    batch_num = fields.Many2one("stock.lot", string="Batch No.", readonly=True)

    def _select_additional_fields(self):
        res = super()._select_additional_fields()
        res['qty_piece'] = """l.piece_qty"""
        res['batch_num'] = """l.batch_num """ 
        return res

    def _group_by_sale(self):
        res = super()._group_by_sale()
        res += """,l.piece_qty, l.batch_num"""
        return res
