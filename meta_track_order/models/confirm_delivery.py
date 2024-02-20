from datetime import datetime, timedelta

from odoo import models, api, fields, _
from odoo.exceptions import ValidationError


class StockPickingInherit(models.Model):
    _inherit = "stock.picking"

    delivered = fields.Datetime(string="Delivery Date", compute='get_time')

    def get_time(self):
        if self[0]:
            for each_stock_picking in self:
                if each_stock_picking.state != "cancel":
                    self = each_stock_picking
        if self.scheduled_date + timedelta(7) < datetime.today():
            self.delivered = self.scheduled_date + timedelta(7)
        else:
            self.delivered = False


