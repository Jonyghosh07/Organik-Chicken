from odoo import models, fields, api, _


class ResPartner(models.Model):
    _inherit = "res.partner"

    last_delivery_date = fields.Date(string="Last Delivery Date", compute="compute_last_dd")
    last_delivery_prods = fields.Char(string="Last Delivery Items", compute="compute_last_dd")

    def compute_last_dd(self):
        for partners in self:
            sale_orders = self.env['sale.order'].sudo().search([('partner_id', '=', partners.id)])
            if sale_orders:
                partners.last_delivery_date = sale_orders[0].delivery_date
                partners.last_delivery_prods = sale_orders[0].msg_body
            else:
                partners.last_delivery_date = False
                partners.last_delivery_prods = False
