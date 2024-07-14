# -*- coding: utf-8 -*-

from datetime import datetime
from odoo import api,fields, models, _
from odoo.http import request
from odoo.exceptions import AccessDenied, UserError
from odoo.addons.auth_signup.models.res_partner import SignupError, now
import logging
_logger = logging.getLogger(__name__)

class MetaResPartner(models.Model):
    _inherit = 'res.partner'

    otp_varified = fields.Boolean(
        string='Otp Verified', default=False
        )
    
    def send_otp(self):
        send_otp_model = self.env['send.otp']
        otp_model = self.env["meta.otp.auth"]
        for partner in self:
            # email = partner.email
            mobile = partner.email or partner.mobile
            otp = otp_model.search([['partner_id','=', partner.id]], order='create_date desc', limit=1)
            
            if not otp or otp.is_expired():
                otp = otp_model.get_new_otp(partner)
                if mobile:
                    send_otp_model.email_send_otp(partner.name or 'User', otp[0], mobile)
                    resp = [True, 'OTP Sent, Valid for {} seconds'.format(otp[1]), 'success']
                else:
                    resp = [False, 'Please Update Phone no', 'error']
            else:
                resp = [True, 'Already sent an OTP. Please Try after {} seconds'.format(int(otp.expire_time -(datetime.now()- otp.create_date).total_seconds())), 'warning']
            return resp
     

class Users(models.Model):
    _inherit = 'res.users'

    # mobile = fields.Char(string="Mobile Number", default="")

    @api.model
    def _check_credentials(self, password, env):
        totp = request.session.get('otploginobj')
        if totp and request.session.get('radio-otp',None)=='radiotp':
            if password.isdigit() and totp.isdigit():
                    if int(totp) == int(password):
                        request.session['otpverified'] = True
                        self.sudo().partner_id.otp_varified = True
                    else:
                        request.session['otpverified'] = False
                        super(Users, self)._check_credentials(password, env)
            else:
                raise AccessDenied()
        else:
            super(Users, self)._check_credentials(password, env)

    @api.model
    def create(self, vals):
        _logger.warning("User create Values {}".format(vals))
        # vals['mobile'] = vals['mobile']
        if isinstance(vals['login'], (tuple, list)):
            vals['login'] = vals['login'][0]
        else: vals['login'] = vals['login']
        
        res = super(Users, self).create(vals)
        if res.partner_id:
            res.partner_id.write({
                'phone': vals['login']
            })

        return res

    def action_reset_password(self):
        """ create signup token for each user, and send their signup url by email """
        if self.env.context.get('install_mode', False):
            return
        if self.filtered(lambda user: not user.active):
            raise UserError(_("You cannot perform this action on an archived user."))
        # prepare reset password signup
        create_mode = bool(self.env.context.get('create_user'))

        # no time limit for initial invitation, only for reset password
        expiration = False if create_mode else now(days=+1)

        self.mapped('partner_id').signup_prepare(signup_type="reset", expiration=expiration)

        # send message to users with their signup url
        for user in self:
            if not user.email:
                raise UserError(_("Cannot send email: user %s has no email address.", user.name))
            mobile = user.email
            sms_text = self.env['ir.default'].sudo().get('res.config.settings', 'reset_pass_content').replace('<name>', user.name)
            self.env['send.sms'].send_sms(mobile, sms_text)
            _logger.warning("Sending Non Cash Payment SMS-------->")

