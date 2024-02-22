from odoo import models, fields, api, _


class ResPartner(models.Model):
    _inherit = "res.partner"

    # total_due_str = fields.Monetary(string="Total Due", related='total_due', store=True)
    last_delivery_date = fields.Date(string="Last Delivery Date", compute="compute_last_dd", store=True)
    last_delivery_prods = fields.Char(string="Last Delivery Items", compute="compute_last_dd")
    last_delivery_batch = fields.Many2one(comodel_name='stock.lot', string="Last Order Batch", compute="compute_last_ob", store=True)
    
    # @api.depends('total_due')
    # def compute_total_due_str(self):
    #     for partners in self:
    #         if partners.total_due:
    #             partners.total_due_str = partners.total_due
    #         else:
    #             partners.total_due_str = '0.00'

    def compute_last_dd(self):
        for partners in self:
            sale_orders = self.env['sale.order'].sudo().search([('partner_id', '=', partners.id)])
            if sale_orders:
                partners.last_delivery_date = sale_orders[0].delivery_date
                partners.last_delivery_prods = sale_orders[0].msg_body
            else:
                partners.last_delivery_date = False
                partners.last_delivery_prods = False

    def compute_last_ob(self):
        for partners in self:
            sale_order_batch = self.env['sale.order.line'].sudo().search([('order_id.partner_id', '=', partners.id)])
            if sale_order_batch:
                for batch in sale_order_batch:
                    if batch.batch_num:
                        partners.last_delivery_batch = sale_order_batch[0].batch_num.id
            else:
                partners.last_delivery_batch = False