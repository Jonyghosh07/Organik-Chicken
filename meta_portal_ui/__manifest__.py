{
    'name': "Portal UI",
    'summary': """ Customize Portal Page Design....""",
    'description': """ Customize Portal Page Design.... """,
    
    'category': 'Tools',
    'version': '16.0.0.1',
    'license': 'AGPL-3',
    
    'author': 'Metamorphosis Ltd, Ahosan',
    'co-author': "Jony Ghosh",
    'company': 'Metamorphosis',
    
    'depends': ['portal', 'sale_management', 'website_sale_stock', 'meta_customer_fields'],
    'data': [
        'security/ir.model.access.csv',
		'views/portal_view.xml',
		'views/Pending_Deliveries.xml',
		'views/Delivered_Orders.xml',
        'views/subscription_view.xml',
    ],
    'assets': {
        'web.assets_frontend': [
            '/meta_portal_ui/static/src/css/portal_ui.css',
            '/meta_portal_ui/static/src/css/single_pending_deliveries.css',
            '/meta_portal_ui/static/src/css/delivered_orders.css',
            '/meta_portal_ui/static/src/js/sale_order_update.js',
            '/meta_portal_ui/static/src/js/sale_copy.js',
            '/meta_portal_ui/static/src/js/subscription_page.js',
        ],
    },
    
    'installable': True,
    'auto_install': False,
    'application': True,
}
