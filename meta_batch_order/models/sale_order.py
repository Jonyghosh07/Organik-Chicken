from odoo import api, fields, models, _, tools
from odoo.exceptions import UserError
from odoo.http import request
import logging

_logger = logging.getLogger(__name__)


class SaleOrderDetails(models.Model):

    _inherit = "sale.order"

    cus_area = fields.Many2one('res.area', string="Customer Area", related="partner_id.area_id")
    cus_sub_area = fields.Many2one('res.subarea', string="Customer Sub Area", related="partner_id.sub_area_id")

    @api.depends('order_line.piece_qty', 'order_line.product_id')
    def _compute_cart_info(self):
        for order in self:
            order.cart_quantity = int(sum(order.mapped('website_order_line.piece_qty')))
            order.only_services = all(l.product_id.type == 'service' for l in order.website_order_line)

    def _cart_update_order_line(self, product_id, quantity, order_line, **kwargs):
        self.ensure_one()
        kilo_gram = 0
        qty_pcs = 0
        if quantity > 0:
            batches = self.env['stock.lot'].search([('product_id.id', '=', product_id)], order="id asc")
            products = self.env['product.product'].search([('id', '=', product_id)])
            got_batch = False
            if batches:
                for batch in batches:
                    if batch.open_close == 'open' and batch.avail_chick >= quantity and batch.exp_date and batch.exp_date < fields.Date.today():
                        got_batch = True
                        # if batch.avg_wght and batch.avail_chick >= quantity:
                        kilo_gram = quantity * batch.avg_wght
                        qty_pcs = quantity
                        break
                if not got_batch:
                    kilo_gram = quantity * products.weight
                    qty_pcs = quantity
                    logging.info(f"kilo_gram ----------> {kilo_gram}")
                else:
                    kilo_gram = quantity
                    qty_pcs = quantity
            
            elif products:
                kilo_gram = quantity * products.weight
                qty_pcs = quantity
            else:
                kilo_gram = quantity
                qty_pcs = quantity

        if order_line and qty_pcs <= 0:
            # Remove zero or negative lines
            order_line.unlink()
            order_line = self.env['sale.order.line']
        elif order_line:
            # Update existing line
            update_values = self._prepare_order_line_update_values(order_line, qty_pcs, kilo_gram, **kwargs)
            if update_values:
                self._update_cart_line_values(order_line, update_values)
        elif qty_pcs > 0:
            order_line_values = self._prepare_order_line_values(product_id, qty_pcs, kilo_gram, **kwargs)
            order_line = self.env['sale.order.line'].sudo().create(order_line_values)
        return order_line

    def _cart_update(self, product_id, line_id=None, add_qty=0, set_qty=0, **kwargs):
        """ Add or set product quantity, add_qty can be negative """
        self.ensure_one()
        self = self.with_company(self.company_id)

        if self.state != 'draft':
            request.session.pop('sale_order_id', None)
            request.session.pop('website_sale_cart_quantity', None)
            raise UserError(_('It is forbidden to modify a sales order which is not in draft status.'))

        product = self.env['product.product'].browse(product_id).exists()
        if add_qty and (not product or not product._is_add_to_cart_allowed()):
            raise UserError(_("The given product does not exist therefore it cannot be added to cart."))

        if line_id is not False:
            order_line = self._cart_find_product_line(product_id, line_id, **kwargs)[:1]
        else:
            order_line = self.env['sale.order.line']

        try:
            if add_qty:
                add_qty = int(add_qty)
        except ValueError:
            add_qty = 1

        try:
            if set_qty:
                set_qty = int(set_qty)
        except ValueError:
            set_qty = 0

        quantity = 0
        if set_qty:
            quantity = set_qty
        elif add_qty is not None:
            if order_line:
                quantity = order_line.product_uom_qty + (add_qty or 0)
            else:
                quantity = add_qty or 0

        if quantity > 0:
            quantity, warning = self._verify_updated_quantity(
                order_line,
                product_id,
                quantity,
                **kwargs,
            )
        else:
            # If the line will be removed anyway, there is no need to verify
            # the requested quantity update.
            warning = ''

        order_line = self._cart_update_order_line(product_id, quantity, order_line, **kwargs)

        if order_line and order_line.price_unit == 0 and self.website_id.prevent_zero_price_sale:
            raise UserError(_(
                "The given product does not have a price therefore it cannot be added to cart.",
            ))

        return {
            'line_id': order_line.id,
            'quantity': quantity,
            'option_ids': list(set(order_line.option_line_ids.filtered(lambda l: l.order_id == order_line.order_id).ids)),
            'warning': warning,
        }

    def _prepare_order_line_values(self, product_id, quantity, kilo_gram, linked_line_id=False,
        no_variant_attribute_values=None, product_custom_attribute_values=None, **kwargs):
        print("_prepare_order_line_values")
        self.ensure_one()
        product = self.env['product.product'].browse(product_id)

        no_variant_attribute_values = no_variant_attribute_values or []
        received_no_variant_values = product.env['product.template.attribute.value'].browse([
            int(ptav['value'])
            for ptav in no_variant_attribute_values
        ])
        received_combination = product.product_template_attribute_value_ids | received_no_variant_values
        product_template = product.product_tmpl_id

        # handle all cases where incorrect or incomplete data are received
        combination = product_template._get_closest_possible_combination(received_combination)

        # get or create (if dynamic) the correct variant
        product = product_template._create_product_variant(combination)

        if not product:
            raise UserError(_("The given combination does not exist therefore it cannot be added to cart."))

        values = {
            'product_id': product.id,
            'piece_qty': quantity,
            'product_uom_qty': kilo_gram,
            'order_id': self.id,
            'linked_line_id': linked_line_id,
        }

        batches = self.env['stock.lot'].sudo().search([('product_id', '=', product.id)], order="id asc")
        for batch in batches:
            # if batch and batch.avail_chick >= quantity:
            if batch.open_close == 'open' and batch.avail_chick >= quantity and batch.exp_date and batch.exp_date > fields.Date.today():
                values['batch_num'] = batch.id

        # add no_variant attributes that were not received
        for ptav in combination.filtered(
            lambda ptav: ptav.attribute_id.create_variant == 'no_variant' and ptav not in received_no_variant_values
        ):
            no_variant_attribute_values.append({
                'value': ptav.id,
            })

        if no_variant_attribute_values:
            values['product_no_variant_attribute_value_ids'] = [
                fields.Command.set([int(attribute['value']) for attribute in no_variant_attribute_values])
            ]

        # add is_custom attribute values that were not received
        custom_values = product_custom_attribute_values or []
        received_custom_values = product.env['product.template.attribute.value'].browse([
            int(ptav['custom_product_template_attribute_value_id'])
            for ptav in custom_values
        ])

        for ptav in combination.filtered(lambda ptav: ptav.is_custom and ptav not in received_custom_values):
            custom_values.append({
                'custom_product_template_attribute_value_id': ptav.id,
                'custom_value': '',
            })

        if custom_values:
            values['product_custom_attribute_value_ids'] = [
                fields.Command.create({
                    'custom_product_template_attribute_value_id': custom_value['custom_product_template_attribute_value_id'],
                    'custom_value': custom_value['custom_value'],
                }) for custom_value in custom_values
            ]
        return values

    def _prepare_order_line_update_values(
        self, order_line, qty_pcs, kilo_gram, linked_line_id=False, **kwargs
    ):
        self.ensure_one()
        values = {}

        if qty_pcs != order_line.piece_qty:
            values['piece_qty'] = qty_pcs
            values['product_uom_qty'] = kilo_gram
        if linked_line_id and linked_line_id != order_line.linked_line_id.id:
            values['linked_line_id'] = linked_line_id

        return values


class SaleOrderLine(models.Model):

    _inherit = "sale.order.line"

    product_id = fields.Many2one(
        comodel_name='product.product',
        string="Product",
        change_default=True, ondelete='restrict', check_company=True, index='btree_not_null',
        domain="[('sale_ok', '=', True), '|', ('company_id', '=', False), ('company_id', '=', company_id)]")
    batch_num = fields.Many2one("stock.lot", string="Batch No.", domain="[('product_id.product_tmpl_id', '=', product_template_id)]")
    piece_qty = fields.Integer(string="Qty in Pcs")
    product_uom_qty = fields.Float(
        string="Quantity",
        compute='_compute_product_uom_qty',
        digits='Product Unit of Measure', default=1.0,
        store=True, readonly=False, required=True, precompute=True)

    @api.onchange('piece_qty')
    def _compute_product_uom_qty(self):
        for lines in self:
            if lines.batch_num:
                lines.product_uom_qty = lines.piece_qty * lines.batch_num.avg_wght
            if lines.batch_num.unit_price_kg:
                lines.price_unit = lines.batch_num.unit_price_kg

    @api.onchange('product_uom_qty')
    def _onchange_product_uom_qty(self):
        for lines in self:
            if lines.batch_num:
                lines.price_subtotal = lines.product_uom_qty * lines.batch_num.unit_price_kg

    # @api.depends('product_template_id')
    # def _compute_lot_id(self):
    #     for record in self:
    #         _logger.info(f"record ------> {record}")
    #         if record.product_template_id:
    #             _logger.info(f"record has product ------> {record}")
    #             lot_nos = self.env['stock.lot'].sudo().search(
    #                 [("product_id.id", "=", record.product_template_id.product_id.id)])
    #             _logger.info(f"lot_nos ------> {lot_nos}")
    #             lots = []
    #             if lot_nos:
    #                 for lot in lot_nos:
    #                     lots.append(lot.id)
    #             return {'domain': {'batch_num': [('id', 'in', lots)]}}
    #         else:
    #             record.batch_num = False

    @api.onchange('batch_num')
    def _onchange_batch_num(self):
        for record in self:
            lot_no = self.env['stock.lot'].sudo().search([("id", "=", record.batch_num.id)])
            if lot_no.avg_wght and record.piece_qty:
                record.product_uom_qty = lot_no.avg_wght * record.piece_qty
            if lot_no.unit_price_kg:
                record.price_unit = lot_no.unit_price_kg
