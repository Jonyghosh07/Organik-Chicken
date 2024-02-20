{
    'name': "Customer Portal",
    'summary': """
        Customize Customer man portal ....""",
    'description': """
        Customize Customer man portal ....
            """,
    'author': 'Metamorphosis',
    'co-author': "Jony Ghosh",
    'company': 'Metamorphosis',
    'category': 'Tools',
    'version': '16.0.2.0.0',
    'depends': ['portal', 'website_sale', 'contacts', 'base', 'sale', 'web', 'meta_customer_fields', 'meta_area_addition'],
    'data': [
        "views/home_template.xml",
        "views/checkout_details.xml",
        "views/my_account_view.xml",
    ],
    'assets': {
        'web.assets_frontend': [
            'meta_customer_portal/static/src/js/custom_checkout.js',
            'meta_customer_portal/static/src/js/my_details.js',
        ],
    },
    'license': 'LGPL-3',
    'installable': True,
    'auto_install': False,
    'application': True,
}
