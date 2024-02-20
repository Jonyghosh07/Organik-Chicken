from odoo import models, fields, api
from odoo.exceptions import AccessError, UserError, ValidationError
import re


class SaleOrderCustom(models.Model):
    _inherit = "sale.order"
    
    referral_contact = fields.Many2one('res.partner', related='partner_id.referral_contact')