# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
import requests
import base64
import json
from odoo.exceptions import ValidationError
from numpy import random
import logging
import pprint

_logger = logging.getLogger(__name__)


class SendSMS(models.TransientModel):
    _name = "send.sms"
    _description = "Send SMS"

    # @api.multi
    def send_sms(self, number, sms_text):
        elitbuzz_url = "https://msg.elitbuzz-bd.com/smsapi"
        sms_provider = (
            self.env["ir.default"].sudo().get("res.config.settings", "sms_provider")
        )

        if sms_provider == "elitbuzz":
            api_token = (
                self.env["ir.default"]
                .sudo()
                .get("res.config.settings", "elitbuzz_api_token")
            )
            sid = (
                self.env["ir.default"].sudo().get("res.config.settings", "elitbuzz_sid")
            )
            _logger.warning("Number--------------->%s", number)
            _logger.warning("Sms Text--------------->%s", sms_text)

            payload = {
                "api_key": api_token,
                "type": "unicode",
                "contacts": number,
                "senderid": sid,
                "msg": sms_text,
            }
            _logger.warning("Payload--------------->%s", payload)

            r = requests.post(elitbuzz_url, data=payload)

            _logger.warning("Response--------------->%s", r.content)
            _logger.info(
                "Send sms with ElitBuzz ---------->%s", pprint.pformat(r.content)
            )
            params_type = "success"
            params_title = "SMS Sent To The Respective Customer"

        else:
            params_type = "warning"
            params_title = "SMS Couldnot be Sent"
            raise ValidationError(
                "Please Select A SMS Provider First And Give It's API Token/Key"
            )

        client_notify = {
            "name": "Manual SMS",
            "type": "ir.actions.client",
            "tag": "display_notification",
            "params": {
                "title": params_title,
                "type": params_type,
                "sticky": False,
            },
        }

        return [True, client_notify]


class ManualSMS(models.TransientModel):
    _name = "manual.sms"
    _description = "Manual SMS"

    manual_sms_box = fields.Text(string="Manual SMS")

    def _send_manual_sms(self):
        form_view_id = self.env.ref("meta_sms_mod.manual_sms_view_form").id
        return {
            "name": "Manual SMS Action",
            "type": "ir.actions.act_window",
            "view_type": "form",
            "view_mode": "form",
            "res_model": "manual.sms",
            "view_id": form_view_id,
            "target": "new",
        }

    def action_send_manual_sms(self):
        active_so = self.env["sale.order"].browse(self.env.context.get("active_ids"))

        for order in active_so:
            _logger.warning("Hiting Action Send For loop-------->")
            # order.so_manual_sms=self.manual_sms_box
            order._order_manual_msg(so_manual_sms=self.manual_sms_box)
            # order.action_manual_so_msg(so_manual_sms=self.manual_sms_box)

        # Return a message indicating that the manual SMS sending is completed
        return {
            "name": "Manual SMS",
            "type": "ir.actions.client",
            "tag": "display_notification",
            "params": {
                "title": "Manual SMS Sent",
                "type": "success",
                "sticky": False,
            },
        }
