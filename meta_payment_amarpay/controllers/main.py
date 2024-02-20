# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import logging
import pprint
import requests
import werkzeug

from odoo import http
from odoo.http import request
from odoo.exceptions import ValidationError


_logger = logging.getLogger(__name__)


class aamarpayController(http.Controller):
    _notify_url  = '/payment/aamarpay/notify'
    _success_url = '/payment/aamarpay/success'
    _cancel_url  = '/payment/aamarpay/cancel'
    _failed_url  = '/payment/aamarpay/failed'

    def _aamarpay_validate_data(self, **post):
        print("_aamarpay_validate_data")
        resp = post.get('pay_status')
        _logger.info('_aamarpay_validate_data: %s', pprint.pformat(resp))
        if resp:
            if resp in ['Successful']:
                _logger.info('aamarpay: validated data')
            else:
                _logger.warning('aamarpay: Transaction Not Successfull, received %s instead of Successful for transaction %s' % (post['pay_status'], post['mer_txnid']))
        if post.get('mer_txnid'):
            post['reference'] = request.env['payment.transaction'].sudo().search([('reference', '=', post['mer_txnid'])]).reference
            return request.env['payment.transaction'].sudo()._handle_notification_data( 'amrpy',post)
        return False

    def _aamarpay_validate_notification(self, **post):
        print("_aamarpay_validate_notification")
        return ""

    @http.route('/payment/aamarpay/success', type='http', auth='public', csrf=False)
    def aamarpay_success(self, **post):
        """ aamarpay success """
        _logger.info('aamarpay_success; Beginning aamarpay form_feedback with post data %s', pprint.pformat(post))
        self._aamarpay_validate_data(**post)
        return request.redirect('/payment/status')
    
    @http.route('/payment/aamarpay/cancel', type='http', auth='public', csrf=False)
    def aamarpay_cancel(self, **post):
        """ aamarpay return """
        _logger.info('aamarpay_cancel; Beginning aamarpay form_feedback with post data %s', pprint.pformat(post))
        post["transaction_cancelled"] = "true"
        self._aamarpay_validate_data(**post)
        return request.redirect('/payment/process')
    
    @http.route('/payment/aamarpay/failed', type='http', auth='public', csrf=False)
    def aamarpay_failed(self, **post):
        """ aamarpay failed """
        _logger.info('aamarpay_failed; Beginning aamarpay form_feedback with post data %s', pprint.pformat(post))
        # post["transaction_failed"] = "true"
        self._aamarpay_validate_data(**post)
        return request.redirect('/payment/process')

    @http.route('/payment/aamarpay/notify', type='http', auth='public', methods=['POST'], csrf=False)
    def aamarpay_notify(self, **post):
        """ aamarpay IPN. """
        _logger.info('Beginning SSLCOM IPN form_feedback with post data %s', pprint.pformat(post))  # debug
        try:
            self._aamarpay_validate_data(**post)
        except ValidationError:
            _logger.exception('Unable to validate the aamarpay IPN Notification ')
        return ''
