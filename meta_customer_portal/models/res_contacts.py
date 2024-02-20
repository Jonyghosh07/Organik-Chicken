from odoo import fields, models, api

import logging
_logger = logging.getLogger(__name__)


class ResState(models.Model):
    _inherit = 'res.country.state'

    def get_website_sale_ares(self):
        area_ids = self.env['res.area'].sudo().search([('state_id', '=', self.id)])
        return area_ids

    def get_website_sale_sub_areas(self):
        sub_area_ids = self.env['res.subarea'].sudo().search([('area_id', '=', self.id)])
        return sub_area_ids