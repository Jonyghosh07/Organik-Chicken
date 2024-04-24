from odoo import api, fields, models, _

class MetaSMSSettings(models.TransientModel):
    _inherit = 'res.config.settings'
    # _name = 'sms.settings'
    _description='res_config_settings'

    sms_provider = fields.Selection([('elitbuzz', 'ElitBuzz')],                     
        string="SMS Provider")

    elitbuzz_api_token = fields.Char('ElitBuzz API Key')
    elitbuzz_sid = fields.Char('ElitBuzz Sender ID')
        
    reset_pass_msg = fields.Boolean(string="Reset Password SMS")
    reset_pass_content = fields.Text(string='Reset Password SMS Content')
    
    order_cash_msg = fields.Boolean(string="Cash Payment SMS")
    order_cash_content = fields.Text(string='Cash Payment SMS Content')
    
    order_nocash_msg = fields.Boolean(string="Non Cash Payment SMS")
    order_nocash_content = fields.Text(string='Non Cash Payment SMS Content')
    
    order_confirmation_msg = fields.Boolean(string="Order Confirmation SMS")
    order_confirmation_content = fields.Text('Order Confirmation SMS Content')

    invoice_msg = fields.Boolean(string="Invoice SMS")
    invoice_content = fields.Text('Invoice SMS Content')
    
    partner_due_msg = fields.Boolean(string="Partner Due SMS")
    partner_due_msg_content = fields.Text('Partner Due SMS Content')
    #
    # order_confirmation_msg_wod = fields.Boolean(string="Confirmation SMS W/O Delivery Date")
    # order_confirmation_content_wod = fields.Text('Confirmation SMS Content W/O Delivery Date')
    #
    # order_otp_msg = fields.Boolean(string="Order OTP SMS")
    # order_otp_content = fields.Text(string='Order OTP SMS Content')
    

    # @api.multi
    def set_values(self):
        super(MetaSMSSettings, self).set_values()
        IrDefault = self.env['ir.default'].sudo()
        IrDefault.set('res.config.settings','sms_provider', self.sms_provider)
        
        IrDefault.set('res.config.settings','elitbuzz_api_token', self.elitbuzz_api_token)        
        IrDefault.set('res.config.settings','elitbuzz_sid', self.elitbuzz_sid)

        IrDefault.set('res.config.settings','reset_pass_msg', self.reset_pass_msg)
        IrDefault.set('res.config.settings','reset_pass_content', self.reset_pass_content)
        
        IrDefault.set('res.config.settings','order_cash_msg', self.order_cash_msg)
        IrDefault.set('res.config.settings','order_cash_content', self.order_cash_content)
        
        IrDefault.set('res.config.settings','order_nocash_msg', self.order_nocash_msg)
        IrDefault.set('res.config.settings','order_nocash_content', self.order_nocash_content)
        
        IrDefault.set('res.config.settings','order_confirmation_msg', self.order_confirmation_msg)
        IrDefault.set('res.config.settings','order_confirmation_content', self.order_confirmation_content)

        IrDefault.set('res.config.settings', 'invoice_msg', self.invoice_msg)
        IrDefault.set('res.config.settings', 'invoice_content', self.invoice_content)
        
        IrDefault.set('res.config.settings', 'partner_due_msg', self.partner_due_msg)
        IrDefault.set('res.config.settings', 'partner_due_msg_content', self.partner_due_msg_content)

        # IrDefault.set('res.config.settings','order_confirmation_msg_wod', self.order_confirmation_msg_wod)
        # IrDefault.set('res.config.settings','order_confirmation_content_wod', self.order_confirmation_content_wod)
        
        # IrDefault.set('res.config.settings','order_otp_msg', self.order_otp_msg)
        # IrDefault.set('res.config.settings','order_otp_content', self.order_otp_content)
        
        return True

    # @api.multi
    def get_values(self):
        res = super(MetaSMSSettings, self).get_values()
        IrDefault = self.env['ir.default'].sudo()
        res.update({
            'sms_provider':IrDefault.get('res.config.settings','sms_provider', self.sms_provider),
            
            'elitbuzz_api_token':IrDefault.get('res.config.settings','elitbuzz_api_token', self.elitbuzz_api_token),                            
            'elitbuzz_sid':IrDefault.get('res.config.settings','elitbuzz_sid', self.elitbuzz_sid),
                                        
            'reset_pass_msg':IrDefault.get('res.config.settings','reset_pass_msg', self.reset_pass_msg),
            'reset_pass_content':IrDefault.get('res.config.settings','reset_pass_content', self.reset_pass_content),
            
            'order_cash_msg':IrDefault.get('res.config.settings','order_cash_msg', self.order_cash_msg),
            'order_cash_content':IrDefault.get('res.config.settings','order_cash_content', self.order_cash_content),
            
            'order_nocash_msg':IrDefault.get('res.config.settings','order_nocash_msg', self.order_nocash_msg),
            'order_nocash_content':IrDefault.get('res.config.settings','order_nocash_content', self.order_nocash_content),
                        
            'order_confirmation_msg':IrDefault.get('res.config.settings','order_confirmation_msg', self.order_confirmation_msg),
            'order_confirmation_content':IrDefault.get('res.config.settings','order_confirmation_content', self.order_confirmation_content),

            'invoice_msg': IrDefault.get('res.config.settings', 'invoice_msg', self.invoice_msg),
            'invoice_content': IrDefault.get('res.config.settings', 'invoice_content', self.invoice_content),
            
            'partner_due_msg': IrDefault.get('res.config.settings', 'partner_due_msg', self.partner_due_msg),
            'partner_due_msg_content': IrDefault.get('res.config.settings', 'partner_due_msg_content', self.partner_due_msg_content),
            
            # 'order_confirmation_msg_wod':IrDefault.get('res.config.settings','order_confirmation_msg_wod', self.order_confirmation_msg_wod),
            # 'order_confirmation_content_wod':IrDefault.get('res.config.settings','order_confirmation_content_wod', self.order_confirmation_content_wod),
            #
            # 'order_otp_msg':IrDefault.get('res.config.settings','order_otp_msg', self.order_otp_msg),
            # 'order_otp_content':IrDefault.get('res.config.settings','order_otp_content', self.order_otp_content),
        })
        return res
