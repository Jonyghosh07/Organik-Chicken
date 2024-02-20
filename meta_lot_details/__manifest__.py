{
    'name': 'Lot Details',
    'version': '16.0.0.1',
    'category': 'Customization',
    'summary': 'This module show the details of Lots (How much cost and how much sale)....',
    'co_author' : 'Jony',
    'description': """
        This module show the details of Lots (How much cost and how much sale)....
    """,
    'depends': [
        'base', 'sale', 'stock', 'mrp', 'product', 'meta_batch_order',
    ],
    'data': [
        "views/stock_view.xml",
        "views/sale_report_view.xml",
    ],
    'assets': {},
    "sequence": -100,
    'license': 'LGPL-3',
    'application': True,
    'installable': True,
    'auto_install': False,
}