from odoo import models, fields, api
from odoo.exceptions import AccessError, UserError, ValidationError
import re, logging


class ResPartner(models.Model):
    _inherit = "res.partner"

    is_delivery_man = fields.Boolean(string="Is Delivery Man")
    is_subscriber = fields.Boolean(string="Is Subscriber")
    subscription_line = fields.One2many(
        comodel_name="subscription.line", inverse_name="partner_id", string="Products"
    )
    subscription_data = fields.Char(
        string="Subscription Data", compute="_compute_subscription_data", store=True
    )

    last_10_sales = fields.Many2many(
        "sale.order.line",
        compute="_compute_last_10_sale_order_products",
        string="Last 10 Sales",
    )
    referral_contact = fields.Many2one(comodel_name="res.partner", string="Reseller")
    map_url = fields.Char(string="Map URL")
    whatsapp_num = fields.Char(string="WhatsApp Number")
    fb_id = fields.Char(string="Facebook ID")
    bkash_num = fields.Char(string="Bkash Number")
    nagad_num = fields.Char(string="Nagad Number")
    is_wholesaler = fields.Boolean(string="Is Wholesaler")
    customer_type = fields.Selection(
        [("regular", "Regular"), ("dropshipper", "Drop Shipper")],
        string="Customer Type",
    )
    deli_location_type = fields.Selection(
        [
            ("residential", "Residential"),
            ("office", "Office"),
            ("other", "Other"),
        ],
        string="Delivery Location Type",
    )
    remarks = fields.Text(string="Remarks")

    total_due_str = fields.Float(
        string="Total Due", compute="compute_total_due_str", store=True
    )
    last_delivery_date = fields.Date(string="Last Delivery Date")
    last_delivery_prods = fields.Char(string="Last Delivery Items")
    last_delivery_batch = fields.Char(string="Last Order Batch")

    @api.depends(
        "unreconciled_aml_ids",
        "followup_next_action_date",
        "unreconciled_aml_ids.date_maturity",
        "unreconciled_aml_ids.date",
        "unreconciled_aml_ids.company_id",
        "unreconciled_aml_ids.amount_residual",
        "unreconciled_aml_ids.move_id.state",
    )
    @api.depends_context('company', 'allowed_company_ids')
    def compute_total_due_str(self):
        # contacts = self.env['res.partner'].sudo().search([("total_due", ">", 0.0)])
        for partner in self:
            # if self.total_due > 0.0:
            # rounded_total_due = round(partner.total_due, 2)
            partner.total_due_str = round(partner.total_due, 2)
            # else:
            #     partner.total_due_str = 0.0

    @api.depends(
        "subscription_line",
        "is_subscriber",
        "subscription_line.product_id",
        "subscription_line.product_id.name",
        "subscription_line.piece_qty",
    )
    def _compute_subscription_data(self):
        for partner in self:
            subscription_line = partner.subscription_line
            data = ""
            if partner.is_subscriber and subscription_line:
                if len(subscription_line) == 1:
                    # If only one subscription line
                    line = subscription_line[0]
                    data += f"{line.product_id.name} ({line.piece_qty})"
                else:
                    # If more than one subscription line
                    for line in subscription_line:
                        data += f"{line.product_id.name} ({line.piece_qty}), "
                    # Remove the trailing comma and space
                    data = data[:-2]
            partner.subscription_data = data

    def update_total_due_str(self):
        contacts = self.env["res.partner"].sudo().search([("total_due", ">", 0.0)])
        for partner in contacts:
            # if partner.total_due:
            # logging.info(f"partner total due ----------------> {partner.total_due}")
            # rounded_total_due = round(partner.total_due, 2)
            partner.total_due_str = round(partner.total_due, 2)
            # else:
            #     partner.total_due_str = 0.0

    def _compute_last_10_sale_order_products(self):
        for partner in self:
            sale_orders = self.env["sale.order"].search(
                [("partner_id", "=", partner.id)], order="date_order desc", limit=10
            )
            order_lines = []
            for order in sale_orders:
                for line in order.order_line:
                    if line.product_template_id.id != 8:
                        order_lines.append(line.id)

            # Last delivery Date & Products
            last_sale_order = self.env["sale.order"].search(
                [("partner_id", "=", partner.id)], order="date_order desc", limit=1
            )
            last_delivered_batch = ""
            if last_sale_order:
                partner.last_delivery_date = last_sale_order.delivery_date
                partner.last_delivery_prods = last_sale_order.msg_body
                for line in last_sale_order.order_line:
                    if line.batch_num.name:
                        last_delivered_batch += (
                            line.batch_num.name + ", "
                        )  # Concatenate batch numbers with a comma and space
                    else:
                        last_delivered_batch += ""
                last_delivered_batch = last_delivered_batch[
                    :-2
                ]  # Remove the last comma and space
                partner.last_delivery_batch = last_delivered_batch
            else:
                partner.last_delivery_date = ""
                partner.last_delivery_prods = ""
                partner.last_delivery_batch = last_delivered_batch

            partner.last_10_sales = order_lines

    @api.onchange("whatsapp_num")
    def _check_mobile_number(self):
        if self.whatsapp_num:
            if not self.whatsapp_num.isdigit():
                raise ValidationError("WhatsApp number must contain only numbers!")
            elif len(self.whatsapp_num) != 11:
                raise ValidationError("WhatsApp number must be 11 digits long!")

    @api.constrains("whatsapp_num")
    def _check_whatsapp_number(self):
        for record in self:
            if record.whatsapp_num:
                # Remove special characters from the mobile number
                whatsapp_num = re.sub(r"\D", "", record.whatsapp_num)
                if not whatsapp_num.isdigit():
                    raise ValidationError("WhatsApp number must contain only numbers!")
                elif len(whatsapp_num) != 11:
                    raise ValidationError("WhatsApp number must be 11 digits long!")

    @api.onchange("bkash_num")
    def _check_bkash_numbr(self):
        if self.bkash_num:
            if not self.bkash_num.isdigit():
                raise ValidationError("Bkash number must contain only numbers!")
            elif len(self.bkash_num) != 11:
                raise ValidationError("Bkash number must be 11 digits long!")

    @api.constrains("bkash_num")
    def _check_bkash_num(self):
        for record in self:
            if record.bkash_num:
                # Remove special characters from the mobile number
                bkash_num = re.sub(r"\D", "", record.bkash_num)
                if not bkash_num.isdigit():
                    raise ValidationError("Bkash number must contain only numbers!")
                elif len(bkash_num) != 11:
                    raise ValidationError("Bkash number must be 11 digits long!")

    @api.onchange("nagad_num")
    def _check_nagad_numbr(self):
        if self.nagad_num:
            if not self.nagad_num.isdigit():
                raise ValidationError("Nagad number must contain only numbers!")
            elif len(self.nagad_num) != 11:
                raise ValidationError("Nagad number must be 11 digits long!")

    @api.constrains("nagad_num")
    def _check_nagad_num(self):
        for record in self:
            if record.nagad_num:
                # Remove special characters from the mobile number
                nagad_num = re.sub(r"\D", "", record.nagad_num)
                if not nagad_num.isdigit():
                    raise ValidationError("Nagad number must contain only numbers!")
                elif len(nagad_num) != 11:
                    raise ValidationError("Nagad number must be 11 digits long!")
