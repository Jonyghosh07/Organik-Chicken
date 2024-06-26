# -*- coding: utf-8 -*-
import logging
from odoo import api, models, _
import requests
import base64
import json
from odoo.exceptions import ValidationError
from numpy import random

class SendOtp(models.TransientModel):
    _name = 'send.otp'

    # @api.multi
    def email_send_otp(self, userName, otp, mobile):
        if not userName:
            userObj = self.env['res.users'].sudo().search(['|', ('login', '=', mobile), ('mobile', '=', mobile)], limit=1)
            userName = userObj.name
        logging.warning('email_send_otp ------ {} >>> {}'.format(type(otp),otp))

        # if mobile:
        #     uid = self.sudo()._uid
        #     fields = self.sudo()._fields
        #     templateObj = self.env.ref('otp_auth.email_template_edi_otp', raise_if_not_found=False)
        #     print(templateObj)
        #     ctx = dict(templateObj._context or {})
        #     ctx['name'] = userName or 'User'
        #     ctx['otp'] = otp
        #     values = templateObj.sudo().with_context(ctx).generate_email(uid, fields)
        #     values['email_to'] = mobile
        #     mailObj = self.env['mail.mail'].sudo().with_context(ctx).create(values)
        #     mailObj.sudo().send()
        
        if mobile:
            sms_provider = self.env['ir.default'].sudo().get('website.otp.settings', 'sms_provider')
            sms_text = self.env['ir.default'].sudo().get('website.otp.settings', 'otp_content').replace('<otp>', str(otp))
            # provider_url = self.env['ir.default'].sudo().get('website.otp.settings', 'provider_url')
            if(sms_provider == 'elitbuzz'):
                
                api_key = self.env['ir.default'].sudo().get('website.otp.settings', 'elitbuzz_api_key')
                senderid = self.env['ir.default'].sudo().get('website.otp.settings', 'elitbuzz_senderid')
                
                payload = {'contacts': mobile, 'msg': sms_text, 'api_key': api_key, 'type': 'text', 'senderid': senderid}
                print(f"payload ---------------> {payload}")
                
                r = requests.post('https://msg.elitbuzz-bd.com/smsapi', params=payload)
                logging.warning("elitbuzz sms response status_code {} : response text {}".format(r.status_code, r.text))

            elif sms_provider == 'iSMS':
                api_token = self.env['ir.default'].sudo().get('website.otp.settings', 'isms_api_token')
                sid = self.env['ir.default'].sudo().get('website.otp.settings', 'isms_sid')
                csms_id = random.randint(99999999)
                
                payload = {'msisdn': mobile, 'sms': sms_text, 'api_token': api_token, 'type': 'text', 'sid': sid, 'csms_id': csms_id}
                r = requests.post('https://smsplus.sslwireless.com/api/v3/send-sms', params=payload)
                logging.warning("msplus.sslwireless.com sms response status_code {} : response text {}".format(r.status_code, r.text))
        return True
