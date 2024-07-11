# -*- coding: utf-8 -*-
from odoo import http, _
from odoo.http import request
import requests
from odoo.addons.web.controllers.home import Home
from odoo import http
import pyotp
import logging
_logger=logging.getLogger(__name__)


class MetaOtpAuthSignupHome(Home):
    
    @http.route(['/signup/otp'], type='json', auth="public", methods=['POST'])
    def send_verify_otp(self, **kwargs):
        phone = kwargs.get('login')
        if phone:
            otpdata = kwargs.get('otpdata') if kwargs.get('otpdata') else self.getOTPData()
            otp = otpdata[0]
            otp_time = otpdata[1]
            
            sms_provider = request.env['ir.default'].sudo().get('website.otp.settings', 'sms_provider')
            sms_text = request.env['ir.default'].sudo().get('website.otp.settings', 'otp_content').replace('<otp>', str(otp))
            provider_url = request.env['ir.default'].sudo().get('website.otp.settings', 'provider_url')
            
            if(sms_provider == 'elitbuzz'):
                api_key = request.env['ir.default'].sudo().get('website.otp.settings', 'elitbuzz_api_key')
                senderid = request.env['ir.default'].sudo().get('website.otp.settings', 'elitbuzz_senderid')
                payload = {'contacts': phone, 'msg': sms_text, 'api_key': api_key, 'type': 'text', 'senderid': senderid}
                
                r = requests.post(provider_url, params=payload)
                logging.warning("elitbuzz sms response status_code {} : response text {}".format(r.status_code, r.text))
                message = {'status':1, 'message':_("OTP has been sent."), 'otp_time':otp_time, 'login':phone}
            else:
                message = {'status':0, 'message':_("User account does not exist. Please signup for an account else try different email or mobile number."), 'otp_time':0, 'login':phone}
        else:
            message = {'status':0, 'message':_("Enter an email or phone number."), 'otp_time':0, 'login':False}
        return message
    
    
    
    def getOTPData(self):
        otp_time = request.env['ir.default'].sudo().get('website.otp.settings', 'otp_time_limit')
        otp_time = int(otp_time)
        if otp_time < 30:
            otp_time = 30
        #Extra Time added to process OTP
        main_otp_time = otp_time
        totp = pyotp.TOTP(pyotp.random_base32(), interval=main_otp_time)
        otp = totp.now()

        request.session['otploginobj'] = otp
        request.session['otpobj'] = otp
        return [otp, otp_time]
    
    
    
    @http.route(['/verify/signup/otp'], type='json', auth="public", methods=['POST'])
    def signup_verify_otp(self, **kwargs):
        otp = kwargs.get('otp')
        print(f"Inside /verify/signup/otp -----------------> {otp}")
        totp = int(request.session.get('otpobj'))
        print(f"Inside /verify/signup/otp -----------------> {totp}")
        if otp.isdigit():
            return True if totp==int(otp) else False
        else:
            return False 
    
    
    @http.route(['/create/new/user'], type='json', auth="public", methods=['POST'])
    def create_new_user(self, **kwargs):
        login = kwargs.get('login')
        password = kwargs.get('password')
        name = kwargs.get('name')
        if login and password and name:
            user = self.env['res.users'].sudo().create([{
            'name': name,
            'login': login,
            'password': password,
        }])
        print(f"user ------------------> {user.name}")