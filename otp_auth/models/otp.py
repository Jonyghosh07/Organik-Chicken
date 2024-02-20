# -*- coding: utf-8 -*-

from datetime import datetime, timedelta
from odoo import api,fields, models, _
from odoo.http import request
import pyotp

from odoo.exceptions import AccessDenied
from odoo.exceptions import ValidationError

import logging
_logger = logging.getLogger(__name__)


class MetaOtp(models.Model):
    _name= "meta.otp.auth"
    _description = "Otp Records"

    partner_id = fields.Many2one('res.partner', string='Customer', required=True,ondelete='cascade')
    otp = fields.Char(string="Otp")
    expire_time = fields.Integer(string='Expire Time(s)', help='Expire time in Seconds')

    def get_new_otp(self, partner ):
        otp_time = self.env['ir.default'].sudo().get('website.otp.settings', 'otp_time_limit')
        otp_time = int(otp_time)
        if otp_time < 30:
            otp_time = 30
        #Extra Time added to process OTP
        main_otp_time = otp_time
        totp = pyotp.TOTP(pyotp.random_base32(), interval=main_otp_time)
        otp = totp.now()
        _logger.warning('get_new_otp ------ {} >>> {}'.format(type(otp),otp))

        self.create({
            'partner_id': partner.id,
            'otp':otp,
            'expire_time':main_otp_time
        })
        self.env.cr.commit()

        return [otp, main_otp_time]

    def is_expired(self):
        self.ensure_one()
        dt_now = datetime.now()
        expire_time = self.create_date + timedelta(seconds = int(self.expire_time))
        if dt_now > expire_time:
            _logger.warning(">>>>>>>>>>>>OTP Expired<<<<<<<")
            return True
        else:
            _logger.warning(">>>>>>>OTP Not Expired<<<<<<<<<")
            return False
    
    def verify_otp(self, partner_id, otp):
        self = self.sudo()
        result = [False, "Otp Expired!!!. Please send another one.",'error']
        _logger.warning("partner_id: {}, otp: {}".format(partner_id, otp))
        partner_otp = self.search(['&',['partner_id', '=',partner_id], ['otp','=', str(otp)]],order='create_date desc', limit=1)
        if partner_otp:
            partner_otp.sudo().partner_id.otp_varified = True
            result = [True, "Otp Successfully Varified.", 'success']

        else:
            result = [False, "Wrong Otp", 'error']
        _logger.warning("verify_otp------>>>> {}".format(result))
        return result
    
        
    @api.model
    def create(self, values):
        """
            Create a new record for a model ModelName
            @param values: provides a data for new record
    
            @return: returns a id of new record
        """
        otps = self.search([['partner_id', '=',values.get('partner_id')]])
        if otps:
            otps.unlink()

        result = super(MetaOtp, self).create(values)
    
        return result
    

    
    _sql_constraints = [
        (
            'unique_customer',
            'unique(partner_id)',
            _('Already Sent an OTP to this Person.')
        )
    ]
    