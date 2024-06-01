from odoo import fields, models, api
import logging

class SaleOrderFilterWizard(models.TransientModel):
    _name = 'sale.order.filter.wizard'
    _description = 'Sale Order Filter Wizard'

    start_date = fields.Date(string='Start Date', required=True)
    end_date = fields.Date(string='End Date', required=True)
    product_id = fields.Many2one('product.product', string="Product", 
    domain=[('sale_ok','=', True)]
    )
    lot_ids = fields.Many2many(
        'stock.lot', 
        string="Lot"
    )

    @api.onchange('product_id')
    def _onchange_product_id(self):
        if self.product_id:
            return {
                'domain': {
                    'lot_ids': [('product_id', '=', self.product_id.id)]
                }
            }
        else:
            return {
                'domain': {
                    'lot_ids': []
                }
            }

    def apply_date_lot_filter(self):
        sale_records = self.env['sale.order'].sudo()
        filter_domain = sale_records.get_date_range_filter(self.start_date, self.end_date, self.product_id, self.lot_ids)
        filtered_records = sale_records.search(filter_domain)
        filtered_ids = filtered_records.ids

        # Update the context with the filtered record IDs
        context_data = dict(self.env.context, active_ids=filtered_ids)
        logging.info(f"self.env.context------------------>{context_data}")
        return {
            'type': 'ir.actions.act_window',
            'name': 'Sale Order',
            'res_model': 'sale.order',
            'view_mode': 'tree,form',
            'target': 'self',
            'domain': filter_domain,
            'context': context_data,
        }


class PScheduler(models.Model):
    _inherit='sale.order'
    
    # Date Range Filter
    def get_date_range_filter(self, start_date, end_date, product, lots):
        filter_domain = [
            ("date_order", ">=", start_date),
            ("date_order", "<=", end_date),
            ("order_line.product_id.id", "=", product.id),
            ("order_line.batch_num.id", "in", lots.ids),
        ]
        return filter_domain
    
    def open_date_range_wizard(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Select Date Lot',
            'res_model': 'sale.order.filter.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {'active_model': self._name, 'active_ids': self.ids},
        }
