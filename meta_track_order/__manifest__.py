{
    'name': 'Track Order',
    'version': '1.0.0.0',
    "category": 'App',
    'description': """
        Use order number to track products.
    """,
    'author': 'Metamorphosis',
    'co-author': 'Rakin',
    'license': 'AGPL-3',
    'depends': [
        'web',
        'sale',
        'website',
        'stock',
        'delivery',
                ],
    "data": [
        "security/ir.model.access.csv",
        "views/track_order.xml",
        "views/courier_name.xml",
        "views/confirm_delivery.xml",
        ],
    'assets': {
        'web.assets_backend': [
            '/meta_track_order/static/src/css/style.css',
            ],
    },
    'init_xml': [],
    'update_xml': [],
    'demo_xml': [],
    'test': [],
    'installable': True,
    'application': True,
    'auto_install': False,
}
