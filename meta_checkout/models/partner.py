# from numpy.core.defchararray import isnumeric

from odoo.exceptions import ValidationError

from odoo import api, fields, models, _, SUPERUSER_ID


class ContactInherit(models.Model):
    _inherit = 'res.partner'

    phone = fields.Char()

    @api.onchange('phone')
    def get_phone(self):
        if self.phone:
            if len(self.phone) < 11:
                raise ValidationError(_('Phone Number Must Be 11 Digits'))

