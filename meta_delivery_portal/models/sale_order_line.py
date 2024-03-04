from odoo import api, fields, models, _
import logging
from datetime import timedelta
from odoo.exceptions import ValidationError
import re, time
from odoo import SUPERUSER_ID
from textwrap import shorten
from datetime import date, datetime
_logger = logging.getLogger(__name__)


class SaleOrderInherits(models.Model):
    _inherit = "sale.order"

    delivery_date = fields.Date(string="Delivery Date")
    partner_remarks = fields.Text(related='partner_id.remarks', string="Partner Remarks", readonly=True)
    admin_comment = fields.Text(string="Admin Comment")
    delivery_man = fields.Many2one("res.partner", string="Delivery Man", domain="[('is_delivery_man', '=', True)]",
                                   tracking=True)
    payment_option = fields.Selection([
                                        ('cash', 'Cash'),
                                        ('bkash', 'bKash'),
                                        ('bank', 'Bank'),
                                    ], string='Payment Option')
    payment_status = fields.Selection([
                                        ('not_paid', 'Not Paid'),
                                        ('in_payment', 'In Payment'),
                                        ('partial', 'Partially Paid'),
                                        ('paid', 'Fully Paid')
                                    ], string='Payment Status', compute='_compute_payment_status')
    defer_status = fields.Selection([
                                        ('wrong', 'ভুল অর্ডার'),
                                        ('cancel', 'ক্যানসেল অর্ডার'),
                                        ('not_home', 'বাসায় নাই'),
                                        ('not_time', 'সময় পাওয়া যায় নাই'),
                                    ], string='Defer Status', readonly=False, store=True)
    nxt_date_delivery = fields.Date(string='Changed Date of Delivery', states={'not_home': [('readonly', False)]})

    @api.onchange('defer_status')
    def _onchange_defer_status(self):
        if self.defer_status != 'not_home':
            self.nxt_date_delivery = False

    total_payable = fields.Monetary(string="Total Payable", compute='compute_total_payable')
    inv_msg = fields.Text(string="Invoice Message", compute="generate_inv_msg")
    final_due = fields.Monetary(string="Final Due", compute='compute_final_due')
    prev_due = fields.Monetary(string="Prev Partner Due", compute='compute_prev_due')
    receipt_paid = fields.Monetary(string="Paid")
    current_datetime = fields.Char(compute='_compute_current_datetime')
    def _compute_current_datetime(self):
        for record in self:
            _logger.info(f"fields.Datetime.now().strftime('%d/%m/%Y %I:%M %p') -----------------------> {fields.Datetime.now().strftime('%d/%m/%Y %I:%M %p')}")
            record.current_datetime = (fields.Datetime.now()+timedelta(hours=6)).strftime('%d/%m/%Y %I:%M %p')
    msg_body = fields.Text(string="Sale Message", compute="generate_message")
    prod_qty_batch = fields.Text(string="Products", compute="generate_message")
    search_phone = fields.Char(string="Phone Search")
    custom_remarks = fields.Char(string="Remarks")
    customer_area = fields.Char(string="Customer Area")
    customer_sub_area = fields.Char(string="Customer Sub Area")
    cash_total = fields.Monetary(string="Cash Paid", compute="compute_cash_total")

    def generate_inv_msg(self):
        for order in self:
            config_inv_msg = self.env['ir.default'].sudo().get('res.config.settings', 'invoice_content')
            _logger.info(f"config_inv_msg --------------> {config_inv_msg}")
            if config_inv_msg:
                order.inv_msg = config_inv_msg
            else:
                order.inv_msg = ""

    def compute_cash_total(self):
        today = date.today()
        for order in self:
            if order.state == 'sale' and order.delivery_date == today and order.payment_option == 'cash':
                final_due = sum(order.invoice_ids.mapped('amount_residual'))  # Current Invoice Due
                total_amount = sum(order.invoice_ids.mapped('amount_total'))  # Current Invoice total Amount
                paid_amount = total_amount - final_due
                order.cash_total = paid_amount
                _logger.info(f"order.cash_total --------> {order.cash_total}")
            else:
                order.cash_total = 0.00

    @api.onchange('search_phone')
    def _onchange_partner_phone(self):
        for order in self:
            if order.search_phone:
                _logger.info("self.search_phone")
                partners = self.env['res.partner'].sudo().search([])
                partner = []
                for customer in partners:
                    _logger.info(f"partner -------> {partner}")
                    if customer.phone == order.search_phone:
                        partner.append(customer.id)
                res = {'domain': {'partner_id': [('id', 'in', partner)]}}
                return res

    @api.depends('order_line')
    def generate_message(self):
        for order in self:
            order.customer_area = order.partner_id.area_id.name
            order.customer_sub_area = order.partner_id.sub_area_id.name

            message = ""
            prods_qty = ""
            for line in order.order_line:
                if line.product_id.detailed_type == "product":
                    message += f"{line.product_id.name}({line.piece_qty}) "
                    prods_qty += f"{line.product_id.name}({line.piece_qty}):-{line.batch_num.name}\n"
            order.msg_body = message
            order.prod_qty_batch = prods_qty

    @api.onchange('order_line')
    def update_message_on_change(self):
        self.generate_message()

    def compute_final_due(self):
        for order in self:
            if order.total_payable and order.receipt_paid:
                order.final_due = order.total_payable - order.receipt_paid
            else:
                order.final_due = order.total_payable

    def compute_prev_due(self):
        for order in self:
            if order.state not in ['sale']:
                total_due = order.partner_id.total_due
                order.prev_due = total_due

            elif order.state in ['sale']:
                total_due = order.partner_id.total_due  # After Invoice confirmed total Due
                total_amount = sum(order.invoice_ids.mapped('amount_total'))  # Current Invoice total Amount
                if order.receipt_paid:
                    order.prev_due = order.receipt_paid - total_amount + total_due
                else:
                    order.prev_due = total_due - total_amount  # Get due of previous Invoice

    def compute_total_payable(self):
        for order in self:
            if order.prev_due :
                order.total_payable = order.prev_due + order.amount_total
            else:
                order.total_payable = order.amount_total

    def _compute_payment_status(self):
        for order in self:
            related_invoices = self.env['account.move'].search([('line_ids.sale_line_ids.order_id', '=', order.id)])
            payment_state = ''
            for invoice in related_invoices:
                if invoice.payment_state == 'in_payment':
                    payment_state = 'in_payment'
                    break
                elif invoice.payment_state == 'paid':
                    payment_state = 'paid'
                    break
                elif invoice.payment_state == 'partial':
                    payment_state = 'partial'
                    break
                else:
                    payment_state = 'not_paid'
            order.payment_status = payment_state

    @api.model
    def update_delivery_status(self, order_id, status, date):
        order = self.env['sale.order'].sudo().search([('id', '=', order_id)])
        order.defer_status = status
        order.nxt_date_delivery = date

    @api.depends('delivery_date')
    def _compute_delivery_man(self):
        for order in self:
            if order.delivery_date:
                # Calculate the cutoff date (e.g., the day after the selected date)
                cutoff_date = order.delivery_date + timedelta(days=1)
                # Check if the current date is after the cutoff date
                if fields.Datetime.now() > cutoff_date:
                    order.delivery_man = False

    @api.model
    def update_order_lines(self, order_id, lines_to_update):
        order = self.env['sale.order'].sudo().search([('name', '=', order_id)])
        _logger.info(f"order lines_to_update {lines_to_update}")
        if order:
            for j in lines_to_update:
                for i in order.order_line:
                    if i.id == j['id']:
                        i.piece_qty = j['piece_qty']
                        i.product_uom_qty = j['product_uom_qty']
                        i.price_unit = j['price_unit']
        return True

    @api.model
    def update_order_status(self, order_id, fields):
        order = self.env['sale.order'].sudo().search([('id', '=', order_id)])
        pay_opt = fields[0].get('payment_option')
        paid_amount = fields[0].get('received')
        if order:
            if fields[0].get('map_url'):
                order.partner_id.map_url = fields[0].get('map_url')
            order.payment_option = pay_opt
            if pay_opt == 'cash' and paid_amount:
                order.receipt_paid = paid_amount
            else:
                order.receipt_paid = 0.00
                order.final_due = order.total_payable

            order._cashnoncash_payment_sms(fields[0].get('payment_option'))
            order.sudo().action_confirm()
            _logger.info("order confirm ....")

            ready_deliveries = order.picking_ids.filtered(lambda p: p.state == 'assigned')
            _logger.info(f"ready_deliveries .... -> {ready_deliveries}")
            for delivery in ready_deliveries:
                _logger.info(f"delivery .... -> {delivery}")
                for move in delivery.move_ids:
                    _logger.info(f"move .... -> {move}")
                    move.quantity_done = move.product_uom_qty
                    _logger.info(f"move.quantity_done .... -> {move.quantity_done}")
                delivery.with_user(SUPERUSER_ID).button_validate()
                _logger.info(f"delivery validated ....")

            if paid_amount and pay_opt != "cash":
                order.receipt_paid = paid_amount
                _logger.info(f"order.receipt_paid .... {order.receipt_paid}")
                context = {
                    'active_model': 'sale.order',
                    'active_ids': [order.id],
                    'active_id': order.id,
                }
                # Let's do an invoice for a down payment of 50
                downpayment = self.env['sale.advance.payment.inv'].sudo().with_context(context).create({
                    'advance_payment_method': 'delivered',
                })
                # order._cashnoncash_payment_sms(fields[0].get('payment_option'))
                downpayment.create_invoices()
                dp_invoice = order.invoice_ids[0]
                dp_invoice.action_post()

            else:
                order.receipt_paid = paid_amount

                context = {
                    'active_model': 'sale.order',
                    'active_ids': [order.id],
                    'active_id': order.id,
                }
                # Let's do an invoice for a down payment of 50
                downpayment = self.env['sale.advance.payment.inv'].sudo().with_context(context).create({
                    'advance_payment_method': 'delivered',
                })
                downpayment.create_invoices()
                dp_invoice = order.invoice_ids[0]
                dp_invoice.action_post()

                account_journal = self.env['account.journal'].sudo().search([('name', '=', 'Cash')])
                journal_id = account_journal.id
                invoice = self.env['account.move'].sudo().search([('invoice_origin', '=', order.name)], limit=1)
                register_payment = self.env['account.payment.register'].sudo().with_context(
                    active_model='account.move', active_ids=invoice.ids).create({
                    'journal_id': journal_id,
                    'amount': paid_amount,
                })
                register_payment._create_payments()

    @api.model
    def cancel_order_status(self, order_id):
        order = self.env['sale.order'].sudo().search([('id', '=', order_id)])
        if order:
            order.sudo()._action_cancel()
            return True
        else:
            return False
        
        
class SaleOrderLineInherits(models.Model):
    _inherit = "sale.order.line"
    
    scanned_ids = fields.One2many('sale.order.line.barcode.line', 'order_line_id',"Scanned Lines")


class AccountMoveInherits(models.Model):
    _inherit = "account.move"

    payment_option = fields.Char(string='Payment Option', compute="_compute_payment_option", readonly=False, store=True)

    def _compute_payment_option(self):
        for invoices in self:
            sales = self.env['sale.order'].sudo().search([('name', '=', invoices.invoice_origin)])
            invoices.payment_option = sales.payment_option

    def _get_move_display_name(self, show_ref=False):
        self.ensure_one()
        name = ''
        if self.state == 'draft':
            name += {
                'out_invoice': _('Draft Invoice'),
                'out_refund': _('Draft Credit Note'),
                'in_invoice': _('Draft Bill'),
                'in_refund': _('Draft Vendor Credit Note'),
                'out_receipt': _('Draft Sales Receipt'),
                'in_receipt': _('Draft Purchase Receipt'),
                'entry': _('Draft Entry'),
            }[self.move_type]
            name += ' '

        if self.partner_id:
            name += self.partner_id.name  # Use the customer's name as the invoice name

        if show_ref and self.ref:
            name += f' ({shorten(self.ref, width=50)})'

        return name

