from odoo import api, fields, models, _
import logging

_logger = logging.getLogger(__name__)

class MetaMrpProduction(models.Model):
    _inherit = 'mrp.production'