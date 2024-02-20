# -*- coding: utf-8 -*-
#################################################################################
#
#   Copyright (c) 2015-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>)
#   See LICENSE file for full copyright and licensing details.
#   If not, see <https://store.webkul.com/license.html/>
#
#################################################################################

from odoo import api, fields, models, _

class WebsiteOTPSettings(models.TransientModel):
    _inherit = 'res.config.settings'
    _name = 'website.otp.settings'

    signin_auth = fields.Boolean(string="Sign-in Authentication")
    signup_auth = fields.Boolean(string="Sign-up Authentication")
    otp_type = fields.Selection([('4', 'Text'), ('3', 'Password')], string="OTP type",
                                  help="""OTP type for user view.
                                    * [Text] OTP will be visible as text type to the user
                                    * [Password] OTP will be visible as password type to the user""")
    otp_time_limit = fields.Integer('OTP Time Limit (sec)',
                            help="OTP expiry time")
    
    otp_content = fields.Text('OTP Content')
    sms_provider = fields.Selection([('elitbuzz', 'Elitbuzz'), ('infobip', 'Infovip'), ('metasms', 'MetaSMS'), ('isms', 'iSMS')], string="SMS Provider")
    elitbuzz_api_key = fields.Char('API Key', required_if_sms_provider='elitbuzz')
    elitbuzz_senderid = fields.Char('Sender ID', required_if_sms_provider='elitbuzz')
    provider_url = fields.Char('Provider URL', required_if_sms_provider='elitbuzz')
    
    isms_api_token = fields.Char('API Token', required_if_sms_provider='isms')
    isms_sid = fields.Char('Sender ID', required_if_sms_provider='isms')

    # @api.multi
    def set_values(self):
        super(WebsiteOTPSettings, self).set_values()
        IrDefault = self.env['ir.default'].sudo()
        IrDefault.set('website.otp.settings','signin_auth', self.signin_auth)
        IrDefault.set('website.otp.settings','signup_auth', self.signup_auth)
        IrDefault.set('website.otp.settings','otp_time_limit', self.otp_time_limit)
        IrDefault.set('website.otp.settings','otp_type', self.otp_type)
        IrDefault.set('website.otp.settings','otp_content', self.otp_content)
        IrDefault.set('website.otp.settings','sms_provider', self.sms_provider)
        IrDefault.set('website.otp.settings','elitbuzz_api_key', self.elitbuzz_api_key)
        IrDefault.set('website.otp.settings','elitbuzz_senderid', self.elitbuzz_senderid)
        IrDefault.set('website.otp.settings','provider_url', self.provider_url)
        IrDefault.set('website.otp.settings','isms_api_token', self.isms_api_token)
        IrDefault.set('website.otp.settings','isms_sid', self.isms_sid)
        return True

    # @api.multi
    def get_values(self):
        res = super(WebsiteOTPSettings, self).get_values()
        IrDefault = self.env['ir.default'].sudo()
        res.update({
            'signin_auth':IrDefault.get('website.otp.settings','signin_auth', self.signin_auth),
            'signup_auth':IrDefault.get('website.otp.settings','signup_auth', self.signup_auth),
            'otp_type':IrDefault.get('website.otp.settings','otp_type', self.otp_type),
            'otp_content':IrDefault.get('website.otp.settings','otp_content', self.otp_content),
            'sms_provider':IrDefault.get('website.otp.settings','sms_provider', self.sms_provider),
            'elitbuzz_api_key':IrDefault.get('website.otp.settings','elitbuzz_api_key', self.elitbuzz_api_key),
            'elitbuzz_senderid':IrDefault.get('website.otp.settings','elitbuzz_senderid', self.elitbuzz_senderid),
            'provider_url':IrDefault.get('website.otp.settings','provider_url', self.provider_url),
            'isms_api_token':IrDefault.get('website.otp.settings','isms_api_token', self.isms_api_token),
            'isms_sid':IrDefault.get('website.otp.settings','isms_sid', self.isms_sid),
        })
        return res
