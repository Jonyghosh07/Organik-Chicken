from odoo import api, exceptions, fields, models, _


class PortalMixinInherit(models.AbstractModel):
    _inherit = "portal.mixin"

    def get_portal_deliver_url(self,orders, suffix=None, report_type=None, download=None, query_string=None, anchor=None):
        self.ensure_one()
        url = '/my/delivery/%s' %(orders.id) + '%s?access_token=%s%s%s%s%s' % (
            suffix if suffix else '',
            self._portal_ensure_token(),
            '&report_type=%s' % report_type if report_type else '',
            '&download=true' if download else '',
            query_string if query_string else '',
            '#%s' % anchor if anchor else ''
        )
        return url

    def get_done_deliver_url(self,orders, suffix=None, report_type=None, download=None, query_string=None, anchor=None):
        self.ensure_one()
        url = '/done/delivery/%s' %(orders.id) + '%s?access_token=%s%s%s%s%s' % (
            suffix if suffix else '',
            self._portal_ensure_token(),
            '&report_type=%s' % report_type if report_type else '',
            '&download=true' if download else '',
            query_string if query_string else '',
            '#%s' % anchor if anchor else ''
        )
        return url
