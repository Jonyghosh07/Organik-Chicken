from odoo import api, fields, models, _


class ResPartnerInherit(models.Model):
    _inherit = "res.partner"

    show_ribbon = fields.Boolean(string="Unavailable", default=False)
