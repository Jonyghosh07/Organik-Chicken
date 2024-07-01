{
    'name': 'Website Product Page Fields',
    'version': '16.0.0.1',
    'category': 'Customization',
    'summary': 'Single product page fields....',
    'co_author' : 'Jony',
    'description': """
        Single product page fields....
    """,
    'depends': [
        'product', 'website_sale'
    ],
    'data': [
        'views/product_view.xml',
    ],
    'assets': {},
    "sequence": -100,
    'license': 'LGPL-3',
    'application': True,
    'installable': True,
    'auto_install': False,
}