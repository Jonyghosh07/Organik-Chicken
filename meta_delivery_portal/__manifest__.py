{
    'name': "Delivery Portal",
    'summary': """
        Create Delivery man portal ....""",
    'description': """
        Create Delivery man portal ....
            """,
    'author': 'Metamorphosis',
    'co-author': "Jony Ghosh",
    'company': 'Metamorphosis',
    'category': 'Tools',
    'version': '16.0.3.0.0',
    'depends': ['meta_customer_fields', 'portal', 'sale_management', 'meta_otp', 'meta_sms_mod'],
    'data': [
        'security/ir.model.access.csv',
        'views/delivery_order_template.xml',
        'views/done_delivery_order_template.xml',
        'views/portal_template_view.xml',
        'views/delivery_man_view.xml',
    ],
    'assets': {
        'web.assets_frontend': [
            '/meta_delivery_portal/static/src/js/update_sale.js',
            '/meta_delivery_portal/static/src/js/barcode_entry.js',
        ],
        'web.assets_backend': [
            '/meta_delivery_portal/static/src/scss/delivery_portal.scss',
        ],
    },
    'license': 'AGPL-3',
    'installable': True,
    'auto_install': False,
    'application': True,
}
