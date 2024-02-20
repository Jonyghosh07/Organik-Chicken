{
    'name': "Checkout Portal",
    'summary': """
        Customize Checkot portal ....""",
    'description': """
        Customize Checkout portal ....
            """,
    'author': 'Metamorphosis',
    'co-author': "Jony Ghosh",
    'company': 'Metamorphosis',
    'category': 'Tools',
    'version': '16.0.2.0.0',
    'depends': ['portal', 'website_sale'],
    'data': [
        "views/checkout_mod.xml",
    ],
    'assets': {
        'web.assets_backend': [
            "/meta_checkout/static/src/css/phonelength.css"
        ],
    },
    'license': 'LGPL-3',
    'installable': True,
    'auto_install': False,
    'application': True,
}
