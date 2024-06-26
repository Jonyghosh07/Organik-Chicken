# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import logging
from odoo.tools.translate import _
from odoo import api, fields, models
from odoo.exceptions import UserError
_logger = logging.getLogger(__name__)


class PortalWizardUser(models.TransientModel):
    """
        A model to configure users in the portal wizard.
    """

    _inherit = 'portal.wizard.user'
    _description = 'Portal User Config'
    
    
    def _assert_user_email_uniqueness(self):
        """Check that the email can be used to create a new user."""
        self.ensure_one()
        if self.email_state == 'exist':
            raise UserError(_('The contact "%s" has the same email as an existing user', self.partner_id.name))
    
    def _create_user(self):
        """ create a new user for wizard_user.partner_id
            :returns record of res.users
        """
        user = self.env['res.users'].with_context(no_reset_password=True)._create_user_from_template({
            'email': self.email,
            'login': self.email,
            'partner_id': self.partner_id.id,
            'company_id': self.env.company.id,
            'company_ids': [(6, 0, self.env.company.ids)],
        })
        if user.login:
            new_password = user.login[-5:]
            user.password = new_password
        return user