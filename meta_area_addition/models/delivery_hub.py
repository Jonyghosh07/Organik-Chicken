# -*- coding: utf-8 -*-

from odoo import fields, models, api


class DeliveryHub(models.Model):
    _name = "delivery.hub"

    name = fields.Char(string="Name")
    country_id = fields.Many2one("res.country", string="Country")
    state_id = fields.Many2many('res.country.state', string="State", domain="[('country_id', '=', country_id)]")
    area_id = fields.Many2many('res.area', string="Area")

