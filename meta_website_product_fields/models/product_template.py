from odoo import api, fields, models, tools, _


class ProductTemplate(models.Model):
    _inherit = "product.template"

    @tools.ormcache()
    def _get_default_web_uom_id(self):
        # Deletion forbidden (at least through unlink)
        return self.env.ref('uom.product_uom_unit')
    
    
    web_uom_id = fields.Many2one(
        'uom.uom', 'Website UOM',
        default=_get_default_web_uom_id, required=True,
        help="Default unit of measure used for Website Product details.")
    web_uom_name = fields.Char(string='Unit of Measure Name', related='web_uom_id.name', readonly=True)
    web_unit_name = fields.Char(compute='_compute_web_unit_name')
    special_text = fields.Text(string="Special Text")
    
    
    @api.depends('web_uom_name')
    def _compute_web_unit_name(self):
        for product in self:
            product.web_unit_name = product.web_uom_name
    
    
    def _get_combination_info(self, combination=False, product_id=False, add_qty=1, pricelist=False, parent_combination=False, only_template=False):
        """Override for website, where we want to:
            - take the website pricelist if no pricelist is set
            - apply the b2b/b2c setting to the result

        This will work when adding website_id to the context, which is done
        automatically when called from routes with website=True.
        """
        self.ensure_one()
        combination_info = super(ProductTemplate, self)._get_combination_info(
            combination=combination, product_id=product_id, add_qty=add_qty, pricelist=pricelist,
            parent_combination=parent_combination, only_template=only_template)
        
        product = self.env['product.product'].browse(combination_info['product_id']) or self
        combination_info.update(
                web_unit_name=product.web_unit_name,
                special_text=product.special_text,
            )
        
        return combination_info
