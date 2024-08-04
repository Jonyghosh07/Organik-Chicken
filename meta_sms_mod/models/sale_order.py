from odoo import api, fields, models, _
import logging

_logger = logging.getLogger(__name__)


class PortalWizard(models.TransientModel):
    _inherit = "portal.wizard"

    def action_pathao_order(self):
        contact_ids = self.env.context.get("active_ids", [])
        for partner in self.env["res.partner"].sudo().browse(contact_ids):
            if partner.phone:
                self.action_due_message(partner)

    def action_due_message(self, partner):
        partner_due_msg = (
            self.env["ir.default"]
            .sudo()
            .get("res.config.settings", "partner_due_msg_content")
        )
        if partner_due_msg:
            mobile = partner.phone.replace("-", "").replace(" ", "")
            sms_text = partner_due_msg.replace("<name>", partner.name).replace(
                "<due_amount>", str(partner.total_due)
            )
            self.env["send.sms"].send_sms(mobile, sms_text)
            _logger.warning("Sending Due SMS-------->")
        else:
            _logger.warning("Please Enter The Message Text")


class SaleOrder(models.Model):
    _inherit = "sale.order"

    customer_mobile = fields.Char("Mobile", related="partner_id.phone")
    courier_delivery_status = fields.Selection(
        [
            ("pending", "Pending"),
            ("shipped", "Shipped"),
            ("delivered", "Delivered"),
            ("return", "Return"),
        ],
        string="Courier Delivery Status",
        default="pending",
    )
    courier_delivery_comment = fields.Text(string="Comment")
    so_manual_sms = fields.Text(string="Manual Sms")
    due_msg = fields.Text(string="Due Message", compute="generate_due_message")

    # @api.depends('prev_due')
    def generate_due_message(self):
        for order in self:
            if order.prev_due:
                message = f"Your Total Due Tk {int(order.prev_due)} + {int(order.amount_total)} = {int(order.prev_due + order.amount_total)} ।"
                order.due_msg = message
            else:
                message = ""
                order.due_msg = message

    def action_c_shipped(self, field_names=None, arg=False):
        self.write({"courier_delivery_status": "shipped"})

    def action_c_delivered(self, field_names=None, arg=False):
        self.write({"courier_delivery_status": "delivered"})

    def action_c_return(self, field_names=None, arg=False):
        self.write({"courier_delivery_status": "return"})

    # main Manual sms function
    def action_manual_so_msg(self, so_manual_sms):
        order_manual_msg = so_manual_sms
        total_ordered_quantity = sum(self.order_line.mapped("product_uom_qty"))
        ordered_product_categories = ", ".join(
            self.order_line.mapped("product_id.categ_id.name")
        )
        if order_manual_msg:
            if self.commitment_date:
                commitment_date = self.commitment_date.date()
                commitment_date_only = str(commitment_date)
                mobile = self.partner_id.phone.replace("-", "").replace(" ", "")
                sms_text = (
                    order_manual_msg.replace("<name>", self.partner_id.name)
                    .replace("<order_id>", str(self.name))
                    .replace("<total_amount>", str(self.amount_total))
                    .replace("<delivery_date>", commitment_date_only)
                    .replace("<order_quantity>", str(total_ordered_quantity))
                    .replace("<payment_option>", str(self.payment_option))
                )

                self.env["send.sms"].send_sms(mobile, sms_text)
                self.message_post(
                    body=_(
                        "Manual SMS of confirmation Sent to %s (%s) : %s.",
                        self.partner_id.name,
                        mobile,
                        sms_text,
                    )
                )
            else:
                mobile = self.partner_id.phone.replace("-", "").replace(" ", "")
                sms_text = (
                    order_manual_msg.replace("<name>", self.partner_id.name)
                    .replace("<order_id>", str(self.name))
                    .replace("<total_amount>", str(self.amount_total))
                    .replace("<order_quantity>", str(total_ordered_quantity))
                    .replace("<product_category>", ordered_product_categories)
                    .replace("<payment_option>", str(self.payment_option))
                )
                self.env["send.sms"].send_sms(mobile, sms_text)
                self.message_post(
                    body=_(
                        "Manual SMS W/O of confirmation Sent to %s (%s) : %s.",
                        self.partner_id.name,
                        mobile,
                        sms_text,
                    )
                )
        else:
            _logger.warning("Please Enter The Message Text")

    # main Order Confirmation sms function
    def action_confirm_so_msg(self):
        order_confirmation_msg = (
            self.env["ir.default"]
            .sudo()
            .get("res.config.settings", "order_confirmation_content")
        )

        if order_confirmation_msg:
            mobile = self.partner_id.phone.replace("-", "").replace(" ", "")
            sms_text = (
                self.env["ir.default"]
                .sudo()
                .get("res.config.settings", "order_confirmation_content")
                .replace("<name>", self.partner_id.name)
                .replace("<msg_body>", str(self.msg_body))
            )
            _logger.info(f"Confirmation sms_text ----------------> {sms_text}")
            self.env["send.sms"].send_sms(mobile, sms_text)
            self.message_post(
                body=_(
                    "SMS of confirmation Sent to %s (%s) : %s.",
                    self.partner_id.name,
                    mobile,
                    sms_text,
                )
            )
            _logger.warning("Sending Confirmation SMS-------->")
        else:
            _logger.warning("Please Enter The Message Text")

    # Order Cash/Noncash sms function
    def action_cash_noncash_so_msg(self, payment_option):
        order_cash_msg = (
            self.env["ir.default"].sudo().get("res.config.settings", "order_cash_msg")
        )
        order_nocash_msg = (
            self.env["ir.default"].sudo().get("res.config.settings", "order_nocash_msg")
        )

        if order_cash_msg or order_nocash_msg:
            if not payment_option == "cash":
                mobile = self.partner_id.phone.replace("-", "").replace(" ", "")
                print(
                    f"sms_text -------> {self.env['ir.default'].sudo().get('res.config.settings', 'order_nocash_content')}"
                )
                sms_text = (
                    self.env["ir.default"]
                    .sudo()
                    .get("res.config.settings", "order_nocash_content")
                    .replace("<name>", self.partner_id.name)
                    .replace("<order_quantity>", str(self.msg_body))
                    .replace("<total_amount>", str(int(self.amount_total)))
                    .replace("<due_msg>", str(self.due_msg))
                )

                self.env["send.sms"].send_sms(mobile, sms_text)

                self.message_post(
                    body=_(
                        "SMS of Non Cash Payment Sent to %s (%s) : %s.",
                        self.partner_id.name,
                        mobile,
                        sms_text,
                    )
                )

                _logger.warning("Sending Non Cash Payment SMS-------->")
            else:
                mobile = self.partner_id.phone.replace("-", "").replace(" ", "")
                sms_text = (
                    self.env["ir.default"]
                    .sudo()
                    .get("res.config.settings", "order_cash_content")
                    .replace("<name>", self.partner_id.name)
                    .replace("<order_quantity>", str(self.msg_body))
                    .replace("<total_amount>", str(int(self.amount_total)))
                    .replace("<due_msg>", str(self.due_msg))
                    .replace("<receipt_amount>", str(int(self.receipt_paid)))
                )
                self.env["send.sms"].send_sms(mobile, sms_text)
                self.message_post(
                    body=_(
                        "SMS of Cash Payment Sent to %s (%s) : %s.",
                        self.partner_id.name,
                        mobile,
                        sms_text,
                    )
                )
                _logger.warning("Sending Cash Payment SMS-------->")
        else:
            _logger.warning("Please Enter The Message Text")

    # Manual SMS
    def _order_manual_msg(self, so_manual_sms):
        _logger.warning("Starting Manual---->")
        for rec in self:
            _logger.warning("Starting Manual REC-->")
            if rec.partner_shipping_id and rec.partner_shipping_id.phone:
                if rec.state in ["draft"]:
                    rec.action_manual_so_msg(so_manual_sms)
                    # rec.action_manual_so_msg(rec)
                else:
                    _logger.warning("State Not Draft-------------->")
            else:
                _logger.warning(
                    "Customer Don't Have Delivery Address For Manual SMS----->"
                )

    # Confirmation SMS
    def _order_confirmation_msg(self):
        if self.partner_id and self.partner_id.phone:
            if self.state in ["draft"]:
                self.action_confirm_so_msg()
            else:
                _logger.warning(
                    "Something was Wrong during Order Confirmation SMS sending..."
                )
        else:
            _logger.warning("Customer Don't Have  Delivery Address")

    # cash Payment sms
    def _cashnoncash_payment_sms(self, payment_option):
        if self.partner_id and self.partner_id.phone:
            self.action_cash_noncash_so_msg(payment_option)
        else:
            _logger.warning("Customer Don't Have  Delivery Address")

    # send otp
    # def _send_otp(self):
    #     if self.state in ['draft'] and self.partner_id and self.partner_id.phone:
    #         _logger.warning("Sending otp to customer------>")
    #         m_otp=self.env['meta.otp'].sudo().search([("partner_id","=",self.partner_id.id)])
    #
    #         # otp_msg=f"Dear {self.partner_id.name}, Please give the otp: {m_otp.otp} to the delivery man {self.delivery_man.name} to ensure your order {self.name}, Thank you."
    #
    #         otp_msg=self.env['ir.default'].sudo().get('res.config.settings', 'order_otp_msg')
    #
    #         _logger.warning(" OTP-------->%s",m_otp.otp)
    #         # _logger.warning(" OTP SMS Content-------->%s",otp_msg)
    #
    #         total_ordered_quantity = sum(self.order_line.mapped('product_uom_qty'))
    #         _logger.warning("Total Ordered Quantity------>%s",total_ordered_quantity)
    #
    #         if otp_msg:
    #             mobile = self.partner_id.phone.replace('-', '').replace(' ', '')
    #             sms_text = self.env['ir.default'].sudo().get('res.config.settings', 'order_otp_content').replace('<name>', self.partner_id.name).replace('<order_id>', str(self.name)).replace('<total_amount>', str(self.amount_total),).replace('<otp>', m_otp.otp).replace('<order_quantity>', str(total_ordered_quantity)).replace('<product_category>', ordered_product_categories).replace('<payment_option>', str(self.payment_option))
    #
    #             self.env['send.sms'].send_sms(mobile, sms_text)
    #
    #             self.message_post(body=_(
    #                 "SMS of confirmation Sent to %s (%s) : %s.",
    #                 self.partner_id.name, mobile, sms_text,
    #             ))
    #             _logger.warning("Sending OTP SMS-------->%s",sms_text)
    #         else:
    #             _logger.warning("Please Enter The Message Text OTP")
    #     else:
    #         _logger.warning("Not in Draft Mode/no partner_id/No partner Phone Number")

    # Individual Order Send Confirmation SMS and State to Sent
    def action_sent_sms(self):
        self.action_quotation_sent()

    def action_quotation_sent(self):
        for so in self:
            so._order_confirmation_msg()
        res = super(SaleOrder, self).action_quotation_sent()
        return res

    # Order Cancel SMS trigger
    def action_cancel(self):
        for so in self:
            so._order_cancellation_msg()
        res = super(SaleOrder, self).action_cancel()
        return res
    
    # Cancellation SMS
    def _order_cancellation_msg(self):
        if self.partner_id and self.partner_id.phone:
            order_confirmation_msg = (
                self.env["ir.default"]
                .sudo()
                .get("res.config.settings", "order_cancel_content")
            )

            if order_confirmation_msg:
                mobile = self.partner_id.phone.replace("-", "").replace(" ", "")
                sms_text = (
                    self.env["ir.default"]
                    .sudo()
                    .get("res.config.settings", "order_cancel_content")
                    .replace("<name>", self.partner_id.name)
                    .replace("<msg_body>", str(self.msg_body))
                )
                self.env["send.sms"].send_sms(mobile, sms_text)
                self.message_post(
                    body=_(
                        "SMS of order cancellation Sent to %s (%s) : %s.",
                        self.partner_id.name,
                        mobile,
                        sms_text,
                    )
                )
            else:
                _logger.warning("Please Enter The Message Text")
        else:
            _logger.warning("Customer Don't Have  Delivery Address")

    # Send Confirmation SMS and State to Sent in bulk from list action
    def _action_sms_quot_sent(self):
        active_ids = self.env.context.get("active_ids", [])
        for so in self.sudo().browse(active_ids):
            so.action_quotation_sent()
