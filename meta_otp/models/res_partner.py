# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
import logging

_logger = logging.getLogger(__name__)

class MetaResPartner(models.Model):
    _inherit = 'res.partner'

    otp_verified = fields.Boolean(
        string='Otp verified', default=False
        )