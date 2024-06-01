from odoo import models, fields, api, _
import datetime



class ResPartnerInherit(models.Model):
    _inherit = "res.partner"

    del_not_done = fields.Selection([('done', 'Done'), ('not_done', 'Not Done')], string="Delivery Status")
    delivery_batch = fields.Char("Not Delivered Batch", compute="_compute_del_not_done")
    
    def _compute_del_not_done(self):
        today = datetime.date.today()
        tomorrow = today + datetime.timedelta(days=1)
        for contact in self:
            sale_orders = contact.sale_order_ids.filtered(lambda so: so.state in ['sent', 'draft'])
            not_done_picking = False
            not_done_sale = []
            for order in sale_orders:
                if not order.delivery_date:
                    not_done_sale.append(order)
                elif order.delivery_date and order.delivery_date >= tomorrow:
                    not_done_sale.append(order)
                
            batch_date = []
            not_delivered_batch = ""
            if not_done_sale:
                not_done_picking = True
                if len(not_done_sale) == 1:
                    not_done_so = not_done_sale[-1]
                    not_delivered_batch = not_done_so.prod_qty_batch
                    print(f"Single not done so ----------------> {not_delivered_batch}")
                else:
                    for order_del in not_done_sale:
                        for line in order_del.order_line:
                            if line.batch_num.exp_date:
                                batch_date.append((order_del, line.batch_num.exp_date))
            
            min_diff = None
            min_diff_order = None
            if batch_date:
                for order, b_date in batch_date:
                    difference = b_date - today
                    if min_diff is None or difference.days < min_diff:
                        min_diff = difference.days
                        min_diff_order = order
            if min_diff_order:
                not_delivered_batch = min_diff_order.prod_qty_batch

            if not_done_picking:
                contact.del_not_done = "not_done"
            else:
                contact.del_not_done = "done"
            contact.delivery_batch = not_delivered_batch
    