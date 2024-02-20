from odoo import api, fields, models,_
import odoo.addons.decimal_precision as dp
from odoo.exceptions import ValidationError
from datetime import datetime, timedelta
from odoo.exceptions import UserError
import logging
import operator as py_operator
import re
_logger = logging.getLogger(__name__)
OPERATORS = {
    '<': py_operator.lt,
    '>': py_operator.gt,
    '<=': py_operator.le,
    '>=': py_operator.ge,
    '=': py_operator.eq,
    '!=': py_operator.ne
}

class AccountMoveX(models.Model):
    _inherit = "account.move"
    
    inv_paid=fields.Float(string="Invoice Paid",digits=(15,2),compute="get_inv_paid")
    inv_delivery_man=fields.Many2one(comodel_name="res.partner",string="Delivery Man",compute="get_inv_delivery_man")
    inv_sale_id=fields.Many2one(comodel_name="sale.order",string="Sale ID",store=True)
    
    @staticmethod
    def _parse_name_search(name):
        """
        Parse the name to search the taxes faster.
        Technical:  0EUM      => 0%E%U%M
                    21M       => 2%1%M%   where the % represents 0, 1 or multiple characters in a SQL 'LIKE' search.
                    21" M"    => 2%1% M%
                    21" M"co  => 2%1% M%c%o%
        Examples:   0EUM      => VAT 0% EU M.
                    21M       => 21% M , 21% EU M, 21% M.Cocont and 21% EX M.
                    21" M"    => 21% M and 21% M.Cocont.
                    21" M"co  => 21% M.Cocont.
        """
        regex = r"(\"[^\"]*\")"
        list_name = re.split(regex, name)
        for i, name in enumerate(list_name.copy()):
            if not name:
                continue
            if re.search(regex, name):
                list_name[i] = "%" + name.replace("%", "_").replace("\"", "") + "%"
            else:
                list_name[i] = '%'.join(re.sub(r"\W+", "", name))
        return ''.join(list_name)
    
    
    def get_inv_paid(self):
        for rec in self:
            rec.inv_paid = rec.amount_total-rec.amount_residual
    
    def get_inv_delivery_man(self):
        for rec in self:
            if rec.line_ids.sale_line_ids.order_id:
                sale_id=rec.line_ids.sale_line_ids.order_id
                rec.inv_sale_id=sale_id
                if sale_id.delivery_man:
                    rec.inv_delivery_man = sale_id.delivery_man
                else:
                    rec.inv_delivery_man=False
            else:
                rec.inv_sale_id=False
                rec.inv_delivery_man=False
    
    # def _search_inv_delivery_man(self, operator, value):
    #     if operator not in ("ilike", "like") or not isinstance(value, str):
    #         return [('inv_delivery_man', operator, value)]
    #     return [('inv_delivery_man', operator, AccountMoveX._parse_name_search(value))]
    
    # def _search_inv_paid(self, operator, value):
    #     if operator not in ('<', '>', '=', '!=', '<=', '>='):
    #         raise UserError(_('Invalid domain operator %s', operator))
    #     if not isinstance(value, (float, int)):
    #         raise UserError(_('Invalid domain right operand %s', value))
    #     ids = []
        
    #     for dm in self.with_context(prefetch_fields=False).search([], order='id'):
    #         if OPERATORS[operator](dm['inv_paid'], value):
    #             ids.append(dm.id)
    #     return [('id', 'in', ids)]
    
    
class AccountPayX(models.Model):
    _inherit = "account.payment"
    
    pay_sale_order=fields.Many2one(comodel_name="sale.order",string="Sale Order",compute="get_pay_sale_order")
    pay_delivery_man=fields.Many2one(comodel_name='res.partner',string="Delivery Man")
    
    def get_pay_sale_order(self):
        logging.info("get_pay_sale_order Function")
        for rec in self:
            if rec.ref:
                # logging.info(f"get_pay_sale_order Function----REC----->{rec}")
                move=self.env['account.move'].sudo().search([('name','=',rec.ref)])
                # logging.info(f"get_pay_sale_order Function----REC----->{move}")
                if len(move)!=0:
                    # logging.info(f"get_pay_sale_order Function----REC----->{move.line_ids.sale_line_ids.order_id}")
                    rec.pay_sale_order=move.line_ids.sale_line_ids.order_id
                    rec.pay_delivery_man=move.line_ids.sale_line_ids.order_id.delivery_man
                else:
                    rec.pay_sale_order=False
                    rec.pay_delivery_man=False
            else:
                rec.pay_sale_order=False
                rec.pay_delivery_man=False
            
            # if len(rec.reconciled_invoice_ids) == 1:
            #     inv_id=rec.reconciled_invoice_ids
            #     rec.pay_sale_order=inv_id.inv_sale_id
            #     rec.pay_delivery_man=inv_id.inv_sale_id.delivery_man
            #     logging.info(f"get_pay_sale_order Function----REC Sale Order----->{rec.pay_sale_order}")
            # else:
            #     inv_id=self.env['account.move'].sudo().search([('id', 'in', self.reconciled_invoice_ids.ids)])
            #     rec.pay_sale_order=inv_id.inv_sale_id
            #     rec.pay_delivery_man=inv_id.inv_sale_id.delivery_man
            #     logging.info(f"get_pay_sale_order Function----REC Sale Order----->{rec.pay_sale_order}")