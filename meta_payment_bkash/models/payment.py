# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
import logging
import requests
import pprint
import json
from odoo import api, fields, models, _
from odoo.tools.float_utils import float_round
from urllib.parse import urlparse, parse_qs
from werkzeug import urls
from odoo.exceptions import UserError, ValidationError
from odoo.addons.meta_payment_bkash.controllers.main import bkashController
from odoo.http import request
_logger = logging.getLogger(__name__)


class PaymentAcquirer(models.Model):
    _inherit = 'payment.provider'

    code = fields.Selection(selection_add=[('bkash', 'bKash')], ondelete={
                            'bkash': 'set default'})

    bkash_password = fields.Char('bKash Password', groups='base.group_user',
                                 help="Username associated with the merchant account which was shared by bKash during on-boarding.")
    bkash_username = fields.Char('bKash Username', groups='base.group_user',
                                 help="Password associated with the bKash merchant account.")
    bkash_appkey = fields.Char('bKash App Key', groups='base.group_user',
                               help="Application Key value shared by bKash during on-boarding.")
    bkash_appsecret = fields.Char('bKash App Secret', groups='base.group_user',
                                  help="Application Secret value shared by bKash during on-boarding.")

    def _compute_feature_support_fields(self):
        """ Override of `payment` to enable additional features. """
        super()._compute_feature_support_fields()
        self.filtered(lambda p: p.code == 'bkash').update({
            'support_refund': 'full_only',
        })

    def _bkash_get_api_url(self):
        if self.state == 'enabled':
            return 'https://tokenized.pay.bka.sh/v1.2.0-beta'
        else:  # test environment
            return 'https://tokenized.sandbox.bka.sh/v1.2.0-beta'

    def _grant_token_bkash(self):
        self.ensure_one()
        body = {
            "app_key": self.bkash_appkey,
            "app_secret": self.bkash_appsecret,
        }
        headers = {
            'username': self.bkash_username,
            'password': self.bkash_password
        }
        url = self._bkash_get_api_url()
        # _logger.info('bKash Grand Token : Body :\n{}'.format(body))
        token_response = requests.post(
            f'{url}/tokenized/checkout/token/grant', headers=headers, data=json.dumps(body))
        # _logger.info('bKash Grand Token (JSON): :\n%s', pprint.pformat(token_response.text))
        token_response_json = token_response.json()
        if 'statusCode' in token_response_json and token_response_json['statusCode'] == '0000':
            authorization = token_response_json['id_token']
            # _logger.info("Authorization ------------------->", token_response_json['id_token'])
            return authorization
        else:
            _logger.error(f"bkash Grant token Error!!!! {token_response.text}")
            raise ValidationError(
                "Unable to get Grant Token from bKash. Please contact Support.")

    def _get_bkash_header_values(self):
        self.ensure_one()
        authorization = self._grant_token_bkash()
        return {
            'Accept': 'application/json',
            'Content-Type': 'application/json',
            'Authorization': authorization,
            'X-APP-Key': self.bkash_appkey
        }


class PaymentTransaction(models.Model):
    _inherit = 'payment.transaction'

    def _get_specific_rendering_values(self, processing_values):
        res = super()._get_specific_rendering_values(processing_values)
        if self.provider_code != 'bkash':
            return res

        self = self.sudo()
        base_url = self.provider_id.get_base_url()

        rendering_values = {
            'mode': '0011',
            'payerReference': f"{self.partner_phone}",
            "callbackURL": urls.url_join(base_url, bkashController._callback_url),
            'amount': f"{self.amount:.2f}",
            'currency': 'BDT',
            'intent': "sale",
            'merchantInvoiceNumber': self.reference.split("-")[0],
        }

        headers = self.provider_id._get_bkash_header_values()

        url = self.provider_id._bkash_get_api_url()

        _logger.info(
            'bKash Create Payment: Body :\n{}'.format(rendering_values))
        create_response = requests.post(
            f'{url}/tokenized/checkout/create', headers=headers, data=json.dumps(rendering_values))
        _logger.info('bKash Create Payment (JSON): :\n%s',
                     pprint.pformat(create_response.text))
        create_response_json = create_response.json()
        if 'statusCode' in create_response_json and create_response_json['statusCode'] == '0000':
            bkashURL = create_response_json['bkashURL']
            paymentId = create_response_json['paymentID']
            self.provider_reference = paymentId
            url_parsed = urlparse(bkashURL)
            url_query_dict = parse_qs(url_parsed.query) or {}

            rendering_values.update({
                'tx_url': bkashURL.split("?")[0],
                'paymentId': url_query_dict['paymentId'][0] or '',
                'apiVersion': url_query_dict['apiVersion'][0] or '',
                'hash': url_query_dict['hash'][0] or '',
                'mode': url_query_dict['mode'][0] or '',
            })
            for order in self.sale_order_ids.filtered(lambda so: so.state in ['draft']):
                order.action_quotation_sent()
        else:
            self.write({
                'last_state_change': fields.Datetime.now()
            })
            self._set_error(state_message=pprint.pformat(create_response_json))
            _logger.error(
                f"bKash Payment create request failed. response {create_response.text}")
            raise ValidationError(
                "bKash Payment request failed. Please contact Support.")

        _logger.info("rendering_values ------>", rendering_values)
        return rendering_values

    def _handle_notification_data(self, provider_code, notification_data):
        tx = self._get_tx_from_notification_data(
            provider_code, notification_data)
        tx._process_notification_data(notification_data)
        tx._execute_callback()
        return tx

    def _get_tx_from_notification_data(self, provider_code, notification_data):
        """ Find the transaction based on the notification data.

        For a provider to handle transaction processing, it must overwrite this method and return
        the transaction matching the notification data.

        :param str provider_code: The code of the provider handling the transaction.
        :param dict notification_data: The notification data sent by the provider.
        :return: The transaction, if found.
        :rtype: recordset of `payment.transaction`
        """
        if provider_code == "bkash":
            print("_bkash_form_validate")
            reference, paymentId = notification_data.get(
                'reference'), notification_data.get('paymentID')
            if not reference or not paymentId:
                _logger.info('bkash: received data with missing reference (%s) or paymentId (%s)' % (
                    reference, paymentId))
                raise ValidationError(
                    _('bkash: received data with missing reference (%s) or paymentId (%s)') % (reference, paymentId))

            txs = self.env['payment.transaction'].search(
                [('provider_reference', '=', paymentId)])
            if not txs or len(txs) > 1:
                error_msg = _(
                    'bkash: received data for reference %s') % (paymentId)
                logger_msg = 'bkash: received data for reference %s' % (
                    paymentId)
                if not txs:
                    error_msg += _('; no order found')
                    logger_msg += '; no order found'
                else:
                    error_msg += _('; multiple order found')
                    logger_msg += '; multiple order found'
                _logger.error(logger_msg)
                raise ValidationError(error_msg)

            return txs
        else:
            return super(PaymentTransaction, self)._get_tx_from_notification_data(provider_code, notification_data)

    def _send_capture_request(self):
        '''Override for bkash payment gateway'''

        if self.provider_id.code != "bkash":
            return super(PaymentTransaction, self)._send_capture_request()

        # Call the bKash Execute Payment API
        _logger.info(f"Calling bKash Execute Payment API")

        body = {
            "paymentId": self.provider_reference
        }
        headers = self.provider_id._get_bkash_header_values()

        url = self.provider_id._bkash_get_api_url()

        r = requests.post(f'{url}/tokenized/checkout/execute',
                          headers=headers, data=json.dumps(body))
        _logger.info(f'bKash: Execute Payment API response {r.text}')
        validation_res = r.json()
        if 'statusCode' in validation_res and validation_res['statusCode'] == '0000':

            if validation_res['transactionStatus'] in ['Completed']:
                self.write({
                    'provider_reference': json.dumps({'trxID': validation_res.get('trxID'), 'paymentId': validation_res.get('paymentId')}),
                })

                self.sudo()._set_done(state_message=r.text)

                for order in self.sale_order_ids.filtered(lambda so: so.state in ['draft', 'sent']):
                    order.sudo().action_confirm()
                    order.sudo()._send_order_confirmation_mail()
                return

            elif validation_res['transactionStatus'] in ['Initiated']:
                msg = f"bKash: received transactionStatus {validation_res['transactionStatus']} from Execute Payment. Setting as Authorized."
                _logger.info(msg)
                self.sudo()._set_authorized()
                return

            else:
                msg = f"bKash: received unknown transactionStatus {validation_res['transactionStatus']} from Execute Payment. Setting as Pending"
                _logger.info(msg)
                self.sudo()._set_pending(state_message=msg)
                return
        else: 
            error = f'Received "{validation_res["statusMessage"]}" message from bKash for your Transaction.'
            _logger.warning(error)
            self._set_error(state_message=error)
            return

    def _process_notification_data(self, notification_data):
        """ Update the transaction state and the provider reference based on the notification data.

        This method should usually not be called directly. The correct method to call upon receiving
        notification data is :meth:`_handle_notification_data`.

        For a provider to handle transaction processing, it must overwrite this method and process
        the notification data.

        Note: `self.ensure_one()`

        :param dict notification_data: The notification data sent by the provider.
        :return: None
        """
        self.ensure_one()
        if self.state in ['done']:
            _logger.info(
                'Transaction (ref %s) is already Validated. Skipping...', self.reference)
            return

        if self.provider_id.code != "bkash":
            return super(PaymentTransaction, self)._process_notification_data(notification_data)

        status = notification_data.get('status')
        res = {}

        if status in ['success']:
            date_validate = fields.Datetime.now()
            res.update({'last_state_change': date_validate})
            # self.execute_callback()
            self.sudo()._send_capture_request()
            return

        elif status == 'failure':
            error = 'Received %s status for bKash payment %s, set as error' % (
                status, self.reference)
            _logger.warning(error)
            self._set_error(state_message=error)
            return

        elif status == 'cancel':
            error = 'Customer Cancelled the Transaction, Cancelled URL was called from bKash for payment %s' % (
                self.reference)
            _logger.warning(error)
            self._set_canceled(state_message=error)
            return

        else:
            error = 'Received unrecognized status for bKash payment %s: %s, set as error' % (
                self.reference, status)
            _logger.warning(error)
            self._set_error(state_message=error)
            return

    def _send_refund_request(self, amount_to_refund=None):
        """ Request the provider handling the transaction to refund it.

        For a provider to support refunds, it must override this method and make an API request to
        make a refund.

        Note: `self.ensure_one()`

        :param float amount_to_refund: The amount to be refunded.
        :return: The refund transaction created to process the refund request.
        :rtype: recordset of `payment.transaction`
        """
        self.ensure_one()

        if self.provider_code != 'bkash':
            return super()._send_refund_request(amount_to_refund=amount_to_refund)

        # Call the bKash Refund Transaction API
        _logger.info(f"Calling bKash Refund Transaction API")

        body = json.loads(self.provider_reference)

        body.update({
            "amount": f"{self.amount:.2f}",
            "reason": "Customer Returned & Asked for refund",
            "sku": self.reference,
        })
        headers = self.provider_id._get_bkash_header_values()

        url = self.provider_id._bkash_get_api_url()
        _logger.info(f'bKash: Refund Transaction API body {body}')

        rr = requests.post(f'{url}/tokenized/checkout/payment/refund',
                          headers=headers, data=json.dumps(body))
        _logger.info(f'bKash: Refund Transaction API response {rr.text}')
        refund_resp = rr.json()
        refund_tx = self.env['payment.transaction']
        if 'statusCode' in refund_resp and refund_resp['statusCode'] == '0000': 
            refund_tx = self._create_refund_transaction(
                amount_to_refund=amount_to_refund)
            refund_tx._log_sent_message()
            if refund_resp['transactionStatus'] == 'Completed':
                refund_tx._set_done(state_message=rr.text)
                        
        else:
            raise UserError(f"Error From Bkash GateWay!!! ({refund_resp.get('statusCode')}){refund_resp.get('statusMessage')}")
        
        return refund_tx


        # ff = {"statusCode": "0000", "statusMessage": "Successful", "originalTrxID": "AJ520FL916", "refundTrxID": "AJ590FL9UJ",
        #       "transactionStatus": "Completed", "amount": "562.35", "currency": "BDT", "charge": "0.00", "completedTime": "2023-10-05T19:35:02:598 GMT+0600"}
