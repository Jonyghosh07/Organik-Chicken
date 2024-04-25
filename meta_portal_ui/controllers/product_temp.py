# In your Odoo module's controller or route
from odoo import http
import json

class ProductController(http.Controller):
    
    @http.route('/api/get_products', type='http', auth='user')
    def get_products(self):
        Product = http.request.env['product.template']
        products = Product.search([])
        # Serialize product data into JSON format
        products_json = [{'id': product.id, 'name': product.name} for product in products]
        # Return JSON response
        return json.dumps(products_json)
