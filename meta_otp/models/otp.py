# -*- coding: utf-8 -*-

from datetime import datetime, timedelta
from odoo import api, fields, models, _
from odoo.http import request
import pyotp

from odoo.exceptions import AccessDenied
from odoo.exceptions import ValidationError, UserError

import logging

_logger = logging.getLogger(__name__)


class MetaOtpAuth(models.Model):
    _name = "meta.otp"
    _description = "Otp Records"

    partner_id = fields.Many2one('res.partner', string='Customer', required=True, ondelete='cascade')
    otp = fields.Char(string="Otp")
    expire_time = fields.Integer(string='Expire Time(s)', help='Expire time in Seconds')

    @api.model
    def find_partner(self, order_id, phone, mobile):
        order = self.env['sale.order'].sudo().search([('id', '=', order_id)])
        if order and order.partner_id.phone:
            print("Phone and mobile : ", phone)
            # partner_phone = phone[0].get('phone')
            res_partner = order.partner_id
            if res_partner:
                self.get_new_otp(res_partner)
                order._send_otp()

        else:
            raise UserError("Customer Phone number Not Found.")



    def get_new_otp(self, partner):
        otp_time = 30
        # Extra Time added to process OTP
        main_otp_time = otp_time
        totp = pyotp.TOTP(pyotp.random_base32(), interval=main_otp_time, digits=4)
        otp = totp.now()
        _logger.warning('The new generated OTP is :------ {} >>> {}'.format(type(otp), otp))

        self.sudo().create({
            'partner_id': partner.id,
            'otp': otp,
            'expire_time': main_otp_time
        })
        self.env.cr.commit()

        return [otp, main_otp_time]

    def is_expired(self):
        self.ensure_one()
        dt_now = datetime.now()
        expire_time = self.create_date + timedelta(seconds=int(self.expire_time))
        if dt_now > expire_time:
            _logger.warning(">>>>>>>>>>>>OTP Expired<<<<<<<")
            return True
        else:
            _logger.warning(">>>>>>>OTP Not Expired<<<<<<<<<")
            return False

    @api.model
    def verify_otp(self, order_id, otp):
        self = self.sudo()
        order = self.env['sale.order'].sudo().search([('id', '=', order_id)])
        partner_id = order.partner_id.id
        _logger.warning("partner_id: {}, otp: {}".format(partner_id, otp))

        partner_otp = self.search(['&', ['partner_id', '=', partner_id], ['otp', 'in', otp]],
                                  order='create_date desc', limit=1)

        if partner_otp:
            partner_otp.sudo().partner_id.otp_verified = True
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
        otps = self.search([['partner_id', '=', values.get('partner_id')]])
        if otps:
            otps.unlink()

        result = super(MetaOtpAuth, self).create(values)

        return result

    _sql_constraints = [
        (
            'unique_customer',
            'unique(partner_id)',
            _('Already Sent an OTP to this Person.')
        )
    ]
