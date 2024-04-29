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
    def updateSubscription(self, user_id, line_id, piece):
        user = self.env['res.users'].sudo().search([('id', '=', user_id)])
        subscription_line = self.env['subscription.line'].sudo().search([('id', '=', line_id), ('partner_id', '=', user.partner_id.id)])
        if subscription_line and piece:
            subscription_line.write({
                'piece_qty': piece
            })
            return
        else:
            return
    
    @api.model
    def addSubscription(self, user_id, prod_id, piece):
        user = self.env['res.users'].sudo().search([('id', '=', user_id)])
        partner = user.partner_id
        product = self.env['product.template'].sudo().search([('id', '=', prod_id)])
        subscription_found = False
        if partner:
            if not partner.is_subscriber:
                partner.is_subscriber = True
                self.env['subscription.line'].sudo().create({
                        'partner_id': partner.id,
                        'product_id': product.id,
                        'piece_qty': piece
                    })
            else:
                for subscription in partner.subscription_line:
                    if subscription.product_id.id == product.id:
                        subscription_found = True
                        break
                
                if not subscription_found:
                    self.env['subscription.line'].sudo().create({
                        'partner_id': partner.id,
                        'product_id': product.id,
                        'piece_qty': piece
                    })
        return {'subscription_exists': subscription_found}
    
    
    @api.model
    def updateSubscriptionPiece(self, user_id, prod_id, piece):
        user = self.env['res.users'].sudo().search([('id', '=', user_id)])
        partner = user.partner_id
        product = self.env['product.template'].sudo().search([('id', '=', prod_id)])

        if partner:
            for subscription in partner.subscription_line:
                if subscription.product_id.id == product.id:
                    subscription.write({
                        'piece_qty': piece
                    })
                    break
