from odoo import models, fields, api, _
import datetime



class ResPartnerInherit(models.Model):
    _inherit = "res.partner"
    
    @api.model
    def create(self, vals):
        # Get the maximum ref value
        max_ref = self.search([], order='ref desc', limit=1).ref
        vals['ref'] = int(max_ref) + 1 if max_ref else 100001

        return super(ResPartnerInherit, self).create(vals)