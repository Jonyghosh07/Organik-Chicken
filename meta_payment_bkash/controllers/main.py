# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import logging
import pprint
import requests
import werkzeug

from odoo import http
from odoo.http import request
from odoo.exceptions import ValidationError
from odoo.addons.payment.controllers.post_processing import PaymentPostProcessing


_logger = logging.getLogger(__name__)


class bkashController(http.Controller):
    _callback_url = '/payment/bkash/tokenized/callback'

    def _bkash_validate_data(self, **post):
        resp = post.get('status')
        _logger.info('_bkash_validate_data: %s', pprint.pformat(resp))
        if resp:
            if resp in ['success']:
                _logger.info(f'bkash: validated data {post}')
            else:
                _logger.info('bkash: Transaction Not successful, received %s instead of success for paymentId %s' % (
                    post['status'], post['paymentID']))
        if post.get('paymentID'):
            trx = request.env['payment.transaction'].sudo().search(
                [('provider_reference', '=', post['paymentID'])], limit=1)
            if trx:
                post['reference'] = trx.reference
                PaymentPostProcessing.monitor_transactions(trx)
                return request.env['payment.transaction'].sudo()._handle_notification_data('bkash', post)
        return False

    @http.route('/payment/bkash/tokenized/callback', type='http', auth='public', csrf=False)
    def bkash_callback(self, **post):
        _logger.info('Beginning bKash callback with data %s',
                    pprint.pformat(post))  # debug
        try:
            self._bkash_validate_data(**post)
        except ValidationError:
            _logger.exception('Unable to validate the bKash Callback ')
        return request.redirect('/payment/status')
