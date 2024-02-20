from odoo import api, fields, models, _


class SubscriptionLine(models.Model):
    _name = "subscription.line"
    _description = "Subscription Line"

    partner_id = fields.Many2one(
        comodel_name="res.partner",
        string="Partner Reference",
        required=True,
        ondelete="cascade",
        index=True,
        copy=False,
    )
    product_id = fields.Many2one(
        comodel_name="product.product",
        string="Product",
        domain="[('sale_ok', '=', True)]",
    )
    piece_qty = fields.Integer(string="Piece")
    batch_no = fields.Many2one(
        "stock.lot",
        string="Batch",
        domain="[('product_id', 'ilike', 'self.product_id')]",
    )
