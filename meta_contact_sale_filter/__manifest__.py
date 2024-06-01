{
    'name': "Custom Filter in Contact and Sale",
    'summary': """
        Custom Filter in Contact and Sale ....""",
    'description': """
        Custom Filter in Contact and Sale ....
            """,
    'author': 'Metamorphosis',
    'co-author': "Jony Ghosh",
    'company': 'Metamorphosis',
    'category': 'Tools',
    'version': '16.0.0.1',
    'depends': ['contacts', 'sale_stock', 'meta_delivery_portal', 'meta_batch_order'],
    'data': [
        'security/ir.model.access.csv',
        'views/res_partner_view.xml',
        'views/wiz_so_filter.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'meta_contact_sale_filter/static/src/**/*.js',
            'meta_contact_sale_filter/static/src/**/*.xml',
        ],
    },

    'license': 'AGPL-3',
    'installable': True,
    'auto_install': False,
    'application': True,
}
