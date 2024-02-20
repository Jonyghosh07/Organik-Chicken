# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import logging

from hashlib import md5
from werkzeug import urls
from urllib.parse import urlparse, parse_qs
import requests
import pprint
import json

import werkzeug

from odoo.exceptions import UserError, ValidationError
from odoo import api, fields, models, _
from odoo.tools.float_utils import float_round
from odoo.addons.meta_payment_amarpay.controllers.main import aamarpayController as amrpyController

_logger = logging.getLogger(__name__)


class PaymentAcquirer(models.Model):
    _inherit = 'payment.provider'
    
    code = fields.Selection(selection_add=[('amrpy', 'aamarPay')], ondelete={'amrpy': 'set default'})
    
    amrpy_store_id = fields.Char('aamarPay Store ID', groups='base.group_user')
    amrpy_signature_key = fields.Char('aamarPay Signature Key', groups='base.group_user')
        

    def _get_feature_support(self):
        print("_get_feature_support")
        res = super(PaymentAcquirer, self)._get_feature_support()
        res['fees'].append('amrpy')
        return res


class PaymentTransaction(models.Model):
    _inherit = 'payment.transaction'

    # --------------------------------------------------
    # FORM RELATED METHODS
    # --------------------------------------------------
    
    def _get_specific_rendering_values(self, processing_values):
        """ Override of `payment` to return SSLCommerz-specific rendering values.

        Note: self.ensure_one() from `_get_processing_values`.

        :param dict processing_values: The generic and specific processing values of the
                                       transaction.
        :return: The dict of provider-specific processing values.
        :rtype: dict
        """
        
        res = super()._get_specific_rendering_values(processing_values)
        if self.provider_code != 'amrpy':
            return res

        base_url = self.provider_id.get_base_url()
        # The lang is taken from the context rather than from the partner because it is not required
        # to be logged in to make a payment, and because the lang is not always set on the partner.
        
        rendering_values = {
            'store_id': self.provider_id.amrpy_store_id,
            'signature_key': self.provider_id.amrpy_signature_key,
            'tran_id': self.reference,
            'amount': f"{float_round(self.amount,2)}",
            'currency': self.currency_id.name if self.currency_id  else 'BDT',
            'success_url': urls.url_join(base_url, amrpyController._success_url),
            'fail_url': urls.url_join(base_url, amrpyController._failed_url),
            'cancel_url': urls.url_join(base_url, amrpyController._cancel_url),

            # CUSTOMER INFORMATION
            'cus_name': self.partner_name,
            'cus_email': self.partner_email,
            'cus_phone': self.partner_phone,
            'cus_add1': self.partner_address,
            'cus_city': self.partner_city,
            'cus_postcode': self.partner_zip,
            'cus_country': self.partner_country_id and self.partner_country_id.name or '',
            
            #DESCRIPTION
            'desc': f"Customer payment with reference {self.reference}",
            
            #PAYLOAD TYPE
            "type": "json"
        }
        
        headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/json'
            }

            
        url = "https://sandbox.aamarpay.com" if self.provider_id.state == 'test' \
            else "https://secure.aamarpay.com"

        _logger.info('_aamarPay Initiate Payment: Values :\n{}'.format(rendering_values))

        payment_response = requests.post(f'{url}/jsonpost.php', headers=headers, data=json.dumps(rendering_values))
        
        _logger.info('_aamarPay Initiate Payment (JSON): :\n%s', pprint.pformat(payment_response.text))
        
        payment_response_json = payment_response.json()

        if( 'result' in payment_response_json and payment_response_json['result'] == 'true'):  
            payment_url = payment_response_json['payment_url']
            url_parsed = urlparse(payment_url)
            url_query_dict = parse_qs(url_parsed.query) or {} 
            track = url_query_dict['track'][0] if 'track' in url_query_dict else False           
            self.provider_reference = track
                       
            for order in self.sale_order_ids.filtered(lambda so: so.state in ['draft']):
                    order.action_quotation_sent()
            
            rendering_values.update({
                'tx_url': payment_url.split("?")[0],
                'track' : track
            })

            return rendering_values
        else:
            self.write({
                    'last_state_change': fields.Datetime.now()                
                })
            self._set_error(state_message=pprint.pformat(payment_response_json))
            
            raise ValidationError(pprint.pformat(payment_response_json))
    
    
    def _handle_notification_data(self, provider_code, notification_data):
        """ Match the transaction with the notification data, update its state and return it.

        :param str provider_code: The code of the provider handling the transaction.
        :param dict notification_data: The notification data sent by the provider.
        :return: The transaction.
        :rtype: recordset of `payment.transaction`
        """
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
        if provider_code == "amrpy":
            print("_amrpy_form_validate")
            reference, txn_id = notification_data.get('reference'), notification_data.get('mer_txnid')
            if not reference or not txn_id:
                _logger.info('amrpy: received data with missing reference (%s) or txn_id (%s)' % (reference, txn_id))
                raise ValidationError(_('amrpy: received data with missing reference (%s) or txn_id (%s)') % (reference, txn_id))

            txs = self.env['payment.transaction'].search([('reference', '=', txn_id)])
            if not txs or len(txs) > 1:
                error_msg = _('amrpy: received data for reference %s') % (txn_id)
                logger_msg = 'amrpy: received data for reference %s' % (txn_id)
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
        
        if self.provider_id.code != "amrpy":
            return super(PaymentTransaction, self)._process_notification_data(notification_data)
        

        status = notification_data.get('pay_status')
        res = {}
                
        if status in ['Successful']:
            _logger.info('Validated aamarPay payment for tx %s: set as done' % (self.reference))
            date_validate = fields.Datetime.now()
            res.update({'last_state_change': date_validate})
            # self.execute_callback()
            
            # Call the SSLCOM VALIDATION API
            payment_provider = self.provider_id
            
            params = {
                'request_id': notification_data.get('mer_txnid'), 
                'store_id': payment_provider.amrpy_store_id, 
                'signature_key': payment_provider.amrpy_signature_key, 
                'type': 'json'
                }
            headers = {
                'Accept': 'application/json',
                'Content-Type': 'application/json'
                }
            
            url = "https://sandbox.aamarpay.com" if payment_provider.state == 'test' \
            else "https://secure.aamarpay.com"
            
            r = requests.get(f'{url}/api/v1/trxcheck/request.php', headers=headers, params=params)
            _logger.info('aamarPay: Order Validation API %s', r.content)
            validation_res = json.loads(r.content)
            
            if validation_res['pay_status'] in ['Successful']:
                res.update({
                    'provider_reference': 'Bank Tran No: {};\n AamarPay Transaction ID {}'.format(validation_res.get('bank_trxid'), validation_res.get('pg_txnid')) ,
                })
                
                self._set_done()
                
                for order in self.sale_order_ids.filtered(lambda so: so.state in ['draft','sent']):
                    order.action_confirm()
                    order._send_order_confirmation_mail()
            
            elif validation_res['pay_status'] in ['Not-Available']:
                return
                                            
            elif validation_res['pay_status'] in ['Failed']:
                error = 'Received %s pay_status for aamarPay payment %s: But received %s status from Notification, setting as error' % (validation_res['pay_status'],self.reference, status)
                _logger.error(error)                
                self._set_error(state_message=error)
                
        elif status == 'Failed':
            error = 'Received %s status for aamarPay payment %s: %s, set as error' % (status,self.reference, status)
            _logger.error(error)
            self._set_error(state_message=error)
        
        elif notification_data.get('transaction_cancelled') == 'true':
            error = 'Customer Cancelled the Transaction, Cancelled URL was called from aamarPay for payment %s' % (self.reference)
            _logger.error(error)
            self._set_canceled(state_message=error)
            
        # elif notification_data.get('transaction_failed') == 'true':
        #     error = 'The Transaction Failed, Failed URL was called from aamarPay for payment %s' % (self.reference)
        #     _logger.error(error)
        #     self._set_canceled(state_message=error)
            
        else:
            error = 'Received unrecognized status for aamarPay payment %s: %s, set as error' % (self.reference, status)
            _logger.error(error)
            self._set_error(state_message=error)
            _logger.info('ERROR~~~ %s:' % (error))
        
        return self.write(res)
