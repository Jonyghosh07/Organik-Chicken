# -*- coding: utf-8 -*-
from odoo import http, _
from odoo.http import request
from odoo.addons.web.controllers.home import Home, SIGN_UP_REQUEST_PARAMS
from odoo import http
from odoo.addons.website_sale.controllers.main import WebsiteSale
import pyotp
from odoo.exceptions import ValidationError, UserError
import logging

_logger=logging.getLogger(__name__)

SIGN_UP_REQUEST_PARAMS = {'db', 'debug', 'token', 'message', 'error', 'scope', 'mode',
                          'redirect', 'redirect_hostname', 'email', 'name', 'partner_id',
                          'password', 'confirm_password', 'city', 'country_id', 'lang', 'signup_email'}


class MetaAuthSignupHome(Home):
    @http.route(['/otp_auth/generate/otp'], type='json', auth="public", methods=['POST'], website=True)
    def generate_otp(self, **kwargs):
        # email = kwargs.get('email')
        mobile = kwargs.get('email')
        user_obj = False
        if mobile :
            if int(kwargs.get('validUser',0))==0:
               user_obj, message = self.checkExistingUser(**kwargs)
            else:
                message = [1, _("Thanks for the registration."), 0]
            if user_obj and message[0] != 0:
                otpdata = self.getOTPData()
                otp = otpdata[0]
                otp_time = otpdata[1]
                self.sendOTP(otp, **kwargs)
                message = [1, _("OTP has been sent to mobile : {}".format(mobile)), otp_time]
        else:
            message = [0, _("Please enter mobile"), 0]
        return message
    
    def checkExistingUser(self, **kwargs):
        # email = kwargs.get('email', None)
        mobile = kwargs.get('email',None)
        user_obj = request.env["res.users"].sudo().search([("login", "=", mobile)], limit=1)
        message = [1, _("Thanks for the registration."), 0]
        _logger.warning("{}".format(user_obj))
        if not user_obj:
            message = [0, _("No user is found registered using this email or mobile number."), 0]
            return False, message
        return user_obj, message

    def sendOTP(self, otp, **kwargs):
        user_name = kwargs.get('userName')
        # email = kwargs.get('email')
        mobile = kwargs.get('email')
        request.env['send.otp'].email_send_otp(user_name, otp, mobile)
        return True

    @http.route(['/verify/otp'], type='json', auth="public", methods=['POST'], website=True)
    def verify_otp(self, otp=False):
        totp = int(request.session.get('otpobj'))
        if otp.isdigit():
            return True if totp==int(otp) else False
        else:
            return False    

    @http.route(website=True, auth="public", sitemap=False)
    def web_login(self, *args, **kw):
        # response = super(MetaAuthSignupHome, self).web_login(redirect=redirect, *args, **kw)
        response = super(MetaAuthSignupHome, self).web_login(*args, **kw)
        totp = request.session.get('otploginobj')
        password = kw.get('password','***')
        if kw.get('radio-otp')=='radiotp' :
            request.session['radio-otp']='radiotp'
            if totp and totp.isdigit() and password.isdigit():
                if int(totp) != int(password):
                    response.qcontext['error'] = _("Incorrect OTP")
            else:
                response.qcontext['error'] = _("Incorrect OTP")
        else:
            request.session['radio-otp']='radiotp'
        _logger.warning("web_login response ----->>>>> {}".format(response))
        return response

    @http.route('/web/reset_password', type='http', auth='public', website=True, sitemap=False)
    def web_auth_reset_password(self, *args, **kw):
        request.session['radio-otp']=None
        return super(MetaAuthSignupHome, self).web_auth_reset_password(*args, **kw)

    @http.route('/web/signup', type='http', auth='public', website=True, sitemap=False)
    def web_auth_signup(self, *args, **kw):
        request.session['radio-otp']='radiopwd'
        if not kw.get('login'):
            return super(MetaAuthSignupHome, self).web_auth_signup(*args, **kw)
        if kw.get('otp'):
            totp = int(request.session.get('otpobj'))
            if totp == int(kw.get('otp')):
                return super(MetaAuthSignupHome, self).web_auth_signup(*args, **kw)
            else:
                qcontext = self.get_auth_signup_qcontext()
                response = request.render('auth_signup.signup', qcontext)
                response.headers['X-Frame-Options'] = 'DENY'
                return response
        else:
            return super(MetaAuthSignupHome, self).web_auth_signup(*args, **kw)

    def get_auth_signup_qcontext(self):
        """ Shared helper returning the rendering context for signup and reset password """
        _logger.warning("Entered get_auth_signup_qcontext in otp_auth")
        
        qcontext = super(MetaAuthSignupHome, self).get_auth_signup_qcontext()
        # mobile = request.params.get('mobile')
        # qcontext.update({
        #     "mobile" : mobile
        # })
        return qcontext

    @http.route(['/send/otp'], type='json', auth="public", methods=['POST'], website=True)
    def send_otp(self, **kwargs):
        phone = kwargs.get('email')
        if phone:
            # Get mobile number 
            user_data, msg = self.checkExistingUser(**kwargs)
            print("Got phone -------->", phone)
            if user_data and user_data.login:     
                otpdata = kwargs.get('otpdata') if kwargs.get('otpdata') else self.getOTPData()
                otp = otpdata[0]
                otp_time = otpdata[1]
                # Send Login Otp
                request.env['send.otp'].email_send_otp(False, otp, user_data.login)
                message = {"email":{'status':1, 'message':_("OTP has been sent."), 'otp_time':otp_time, 'login':phone}}
            else:
                message = {"email":{'status':0, 'message':_("User account does not exist. Please signup for an account else try different email or mobile number."), 'otp_time':0, 'login':phone}}
        else:
            message = {"email":{'status':0, 'message':_("Enter an email or phone number."), 'otp_time':0, 'login':False}}
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
    
    def do_signup(self, qcontext):       
        values = {key: qcontext.get(key) for key in ('login', 'name', 'password')}
        if not values:
            raise UserError(_("The form was not properly filled in."))
        if values.get('password') != qcontext.get('confirm_password'):
            raise UserError(_("Passwords do not match; please retype them."))
        if values.get('mobile'):
            values['mobile'] = values['mobile'],
        self._signup_with_values(qcontext.get('token'), values)
        request.env.cr.commit()
        
    @http.route(['/get/login'], type='json', auth="public", methods=['POST'], website=True)
    def get_login(self, **kwargs):
        email = kwargs.get('email')
        if email:
            # Get mobile number 
            # user_data = request.env["res.users"].sudo().search([('mobile', '=', email)],limit=1)
            user_data, msg = self.checkExistingUser(**kwargs)

            if user_data and user_data.login:      
                # Send Login Otp
                message = {"email":{'status':1, 'message':_("OTP has been sent to : {}.".format(email)), 'login':user_data.login}}
            else:
                message = {"email":{'status':0, 'message':_("User account does not exist. Please signup for an account else try different email or mobile number."), 'otp_time':0, 'login':email}}
        else:
            message = {"email":{'status':0, 'message':_("Enter an email or phone number."), 'otp_time':0, 'login':False}}
        return message

    @http.route(['/otp/verification'], type='http', auth="public", website=True)
    def otp_verifcation(self, redirect=None):
        partner = request.env.user.partner_id
        if not partner:
            return request.redirect('/web/login')
        resp = partner.send_otp()         
        redirect= redirect or '/my'
        return request.render('otp_auth.otp_verify_after_signup', {'partner':partner, 'resp':resp, 'redirect':redirect})

    # @http.route(['/otp/send'], type='http', auth="public", website=True)
    # def otp_send(self, redirect=None):
    #     partner = request.env.user.partner_id
    #     if not partner:
    #         return request.redirect('/web/login')
    #     resp = partner.send_otp()
    #     redirect= redirect or '/my'
    #     return request.render('otp_auth.otp_verify_after_signup', {'partner':partner,'resp':resp, 'redirect':redirect})
        
    
    @http.route(['/otp/verify'], type='http', auth="public", methods=['POST'], website=True)
    def verify_otp(self, redirect=None, otp=False, **post):
        totp = post.get('otpin')
        partner_id = int(post.get('partner_id'))
        partner = request.env.user.partner_id
        _logger.warning("totp----------->>>>> {}".format(totp))
        _logger.warning("redirect----------->>>>> {}".format(redirect))
        resp = request.env['meta.otp.auth'].verify_otp(partner_id, totp)
        redirect= redirect or '/my'
        if resp[0] == True and  partner_id == partner.id:
            return request.redirect(redirect)
        else:
            return request.render('otp_auth.otp_verify_after_signup', {'partner':partner,'resp':resp, 'redirect':redirect})
        

class OtpAuthWebsiteSale(WebsiteSale):
    @http.route(['/shop/checkout'], type='http', auth="public", website=True, sitemap=False)
    def checkout(self, **post):
        partner = request.env.user.partner_id
        if not partner.otp_varified:
            # return request.redirect("/otp/verification?redirect={}".format('/shop/checkout'))
            return request.redirect("/web/signup")

        res = super(OtpAuthWebsiteSale, self).checkout()        
        return res