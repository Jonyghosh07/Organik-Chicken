# -*- coding: utf-8 -*-
from odoo import fields, models, api

import logging

_logger = logging.getLogger(__name__)


class Contacts(models.Model):
    _inherit = "res.partner"

    area_id = fields.Many2one('res.area', 'Area')
    sub_area_id = fields.Many2one('res.subarea')


class Area(models.Model):
    _name = 'res.area'

    name = fields.Char('Area Name')
    sub_area_id = fields.One2many('res.subarea', 'area_id')
    areacode_id = fields.Many2one('res.areacode')
    state_id = fields.Many2one('res.country.state', string="District")


class SubArea(models.Model):
    _name = 'res.subarea'

    name = fields.Char("Sub Area Name")
    area_id = fields.Many2one("res.area", "Area")
    state_id = fields.Many2one('res.country.state', related="area_id.state_id", string="District")


class Areacode(models.Model):
    _name = 'res.areacode'

    name = fields.Char('Area code')
    area_id = fields.One2many('res.area', 'areacode_id', 'area')


class ResState(models.Model):
    _inherit = 'res.country.state'

    def get_website_sale_ares(self):
        area_ids = self.env['res.area'].sudo().search([('state_id', '=', self.id)])
        return area_ids
