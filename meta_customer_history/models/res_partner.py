from odoo import models, fields, api, _


class ResPartner(models.Model):
    _inherit = "res.partner"

    total_due_str = fields.Char(string="Total Due", compute='compute_total_due_str', store=True)
    last_delivery_date = fields.Date(string="Last Delivery Date", compute="compute_last_dd", store=True)
    last_delivery_prods = fields.Char(string="Last Delivery Items", compute="compute_last_dd", store=True)
    last_delivery_batch = fields.Char(string="Last Order Batch", compute="compute_last_ob", store=True)
    
    @api.depends('total_due')
    def compute_total_due_str(self):
        for partners in self:
            if partners.total_due:
                # Round the total_due to two decimal places
                rounded_total_due = round(partners.total_due, 2)
                # Convert the rounded total_due to a string with two decimal places
                partners.total_due_str = '{:.2f}'.format(rounded_total_due)
            else:
                partners.total_due_str = '0.00'

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
        for partner in self:
            last_delivered_batch = ''
            sale_order = self.env['sale.order'].sudo().search([('partner_id', '=', partner.id), ('state', '=', 'sale')], order='date_order desc', limit=1)
            if sale_order:
                # Get the last sale order for the partner
                for line in sale_order.order_line:
                    last_delivered_batch += line.batch_num.name + ', '  # Concatenate batch numbers with a comma and space
                last_delivered_batch = last_delivered_batch[:-2]  # Remove the last comma and space
            partner.last_delivery_batch = last_delivered_batch

