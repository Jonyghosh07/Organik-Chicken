from odoo import api, fields, models, _
import logging

class ResPartnerInherits(models.Model):
    _inherit = "res.partner"
    
    @api.model
    def deleteSubscription(self, line_id):
        subscription_line = self.env['subscription.line'].sudo().search([('id', '=', line_id)])
        if subscription_line:
            subscription_line.unlink()
            return
        else:
            return
    
    @api.model
    def updateSubscription(self, line_id, piece):
        subscription_line = self.env['subscription.line'].sudo().search([('id', '=', line_id)])
        if subscription_line and piece:
            subscription_line.write({
                'piece_qty': piece
            })
            return
        else:
            return
    
    @api.model
    def addSubscription(self, user_id, prod_id, piece):
        partner = self.sudo().search([('user_ids', 'in', user_id)])
        product = self.env['product.template'].sudo().search([('id', '=', prod_id)])
        if partner:
            if not partner.is_subscriber:
                partner.is_subscriber = True
            self.env['subscription.line'].sudo().create({
                'partner_id': partner.id,
                'product_id': product.id,
                'piece_qty': piece
            })
            return
        else:
            return