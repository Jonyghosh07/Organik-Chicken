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

    code = fields.Selection(selection_add=[('bkash', 'bKash')], ondelete={'bkash': 'set default'})

    bkash_password = fields.Char('bKash Password', groups='base.group_user',help="Username associated with the merchant account which was shared by bKash during on-boarding.")
    bkash_username = fields.Char('bKash Username', groups='base.group_user',help="Password associated with the bKash merchant account.")
    bkash_appkey = fields.Char('bKash App Key', groups='base.group_user',help="Application Key value shared by bKash during on-boarding.")
    bkash_appsecret = fields.Char('bKash App Secret', groups='base.group_user', help="Application Secret value shared by bKash during on-boarding.")

    def _get_feature_support(self):
        print("_get_feature_support")
        res = super(PaymentAcquirer, self)._get_feature_support()
        res['fees'].append('bkash')
        return res


class PaymentTransaction(models.Model):
    _inherit = 'payment.transaction'

    def _get_specific_rendering_values(self, processing_values):
        res = super()._get_specific_rendering_values(processing_values)
        if self.provider_code != 'bkash':
            return res
        base_url = self.provider_id.get_base_url()
        authorization = self._grant_token_bkash()

        rendering_values = {
            'mode': '0011',
            'payerReference': f"{self.partner_phone}",
            "callbackURL": urls.url_join(base_url, bkashController._callback_url),
            'amount': f"{float_round(self.amount, 2)}",
            'currency': 'BDT',
            'intent': "sale",
            'merchantInvoiceNumber': self.reference.split("-")[0],
        }
        headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/json',
            'Authorization': authorization,
            'X-APP-Key': self.provider_id.bkash_appkey
        }
        url = "https://.pay.bka.sh" if self.provider_id.state == 'test' \
            else "https://tokenized.sandbox.bka.sh/v1.2.0-beta"

        _logger.info('bKash Create Payment: Body :\n{}'.format(rendering_values))
        create_response = requests.post(f'{url}/tokenized/checkout/create', headers=headers, data=json.dumps(rendering_values))
        _logger.info('bKash Create Payment (JSON): :\n%s', pprint.pformat(create_response.text))
        create_response_json = create_response.json()
        if 'statusCode' in create_response_json and create_response_json['statusCode'] == '0000':
            bkashURL = create_response_json['bkashURL']
            paymentID = create_response_json['paymentID']
            self.provider_reference = paymentID
            url_parsed = urlparse(bkashURL)
            url_query_dict = parse_qs(url_parsed.query) or {}

            rendering_values.update({
                'tx_url': bkashURL.split("?")[0],
                'paymentID':url_query_dict['paymentID'][0] or '',
                'apiVersion':url_query_dict['apiVersion'][0] or '',
                'hash':url_query_dict['hash'][0] or '',
                'mode':url_query_dict['mode'][0] or '',
            })
            for order in self.sale_order_ids.filtered(lambda so: so.state in ['draft']):
                order.action_quotation_sent()
        else:
            self.write({
                'last_state_change': fields.Datetime.now()
            })
            self._set_error(state_message=pprint.pformat(create_response_json))
            _logger.error(f"bKash Payment create request failed. response {create_response.text}")
            raise ValidationError("bKash Payment request failed. Please contact Support.")

        print("rendering_values ------>", rendering_values)
        return rendering_values

    def _grant_token_bkash(self):
        body = {
            "app_key": self.provider_id.bkash_appkey,
            "app_secret": self.provider_id.bkash_appsecret,
        }
        headers = {
            'username': self.provider_id.bkash_username,
            'password': self.provider_id.bkash_password
        }
        url = "https://.pay.bka.sh" if self.provider_id.state == 'test' \
            else "https://tokenized.sandbox.bka.sh/v1.2.0-beta"
        _logger.info('bKash Grand Token : Body :\n{}'.format(body))
        token_response = requests.post(f'{url}/tokenized/checkout/token/grant', headers=headers, data=json.dumps(body))
        _logger.info('bKash Grand Token (JSON): :\n%s', pprint.pformat(token_response.text))
        token_response_json = token_response.json()
        if 'statusCode' in token_response_json and token_response_json['statusCode'] == '0000':
            authorization = token_response_json['id_token']
            # _logger.info("Authorization ------------------->", token_response_json['id_token'])
            return authorization
        else:
            _logger.error(f"bkash Grant token Error!!!! {token_response.text}")
            raise ValidationError("Unable to get Grant Token from bKash. Please contact Support.")


    def _handle_notification_data(self, provider_code, notification_data):
        tx = self._get_tx_from_notification_data(provider_code, notification_data)
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
            reference, paymentid = notification_data.get('reference'), notification_data.get('paymentID')
            if not reference or not paymentid:
                _logger.info('bkash: received data with missing reference (%s) or paymentid (%s)' % (reference, paymentid))
                raise ValidationError(
                    _('bkash: received data with missing reference (%s) or paymentid (%s)') % (reference, paymentid))

            txs = self.env['payment.transaction'].search([('provider_reference', '=', paymentid)])
            if not txs or len(txs) > 1:
                error_msg = _('bkash: received data for reference %s') % (paymentid)
                logger_msg = 'bkash: received data for reference %s' % (paymentid)
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
            _logger.info('Transaction (ref %s) is already Validated. Skipping...', self.reference)
            return True

        if self.provider_id.code != "bkash":
            return super(PaymentTransaction, self)._process_notification_data(notification_data)

        status = notification_data.get('status')
        res = {}

        if status in ['success']:
            date_validate = fields.Datetime.now()
            res.update({'last_state_change': date_validate})
            # self.execute_callback()

            # Call the bKash Query Payment API
            _logger.info(f"Calling bKash Query Payment API")
            payment_provider = self.provider_id
            authorization = self._grant_token_bkash()

            params = {
                "paymentID": f"{notification_data.get('paymentID')}"
            }
            headers = {
                'Accept': 'application/json',
                'Content-Type': 'application/json',
                'Authorization': authorization,
                'X-APP-Key': payment_provider.bkash_appkey
            }

            url = "https://.pay.bka.sh" if payment_provider.state == 'test' \
                else "https://tokenized.sandbox.bka.sh/v1.2.0-beta"

            r = requests.post(f'{url}/tokenized/checkout/payment/status', headers=headers, data=json.dumps(params))
            _logger.info(f'bKash: Query Payment API response {r.content}' )
            validation_res = r.json()

            if validation_res['transactionStatus'] in ['Completed']:
                res.update({
                    'provider_reference': f"bKash transaction ID: {validation_res.get('trxID')};\n bKash paymentID {validation_res.get('paymentID')}",
                })

                self.sudo()._set_done()

                for order in self.sale_order_ids.filtered(lambda so: so.state in ['draft', 'sent']):
                    order.sudo().action_confirm()
                    order.sudo()._send_order_confirmation_mail()

            elif validation_res['transactionStatus'] in ['Initiated']:
                _logger.info(f"Skipping bKash payment received transactionStatus {validation_res['transactionStatus']} from Query Payment.")
                return False

            else:
                _logger.info(f"Skipping bKash payment, received unknown transactionStatus {validation_res['transactionStatus']} from Query Payment.")
                return False


        elif status == 'failure':
            error = 'Received %s status for bKash payment %s, set as error' % (status, self.reference)
            _logger.warning(error)
            self._set_error(state_message=error)

        elif status == 'cancel':
            error = 'Customer Cancelled the Transaction, Cancelled URL was called from bKash for payment %s' % (
                self.reference)
            _logger.warning(error)
            self._set_canceled(state_message=error)


        else:
            error = 'Received unrecognized status for bKash payment %s: %s, set as error' % (self.reference, status)
            _logger.warning(error)
            self._set_error(state_message=error)

        return self.write(res)