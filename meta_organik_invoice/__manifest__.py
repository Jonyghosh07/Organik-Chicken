{
    'name': 'Invoice Report',
    'version': '16.0',
    'category': 'Customization',
    'summary': 'Organik Chicken Invoice report customization....',
    'co_author' : 'Jony',
    'description': """

    """,
    'depends': [
        'base','sale','account', 'stock_account'
    ],
    'data': [
        'report/invoice_report.xml',
        'data/paper_format.xml',
    ],
    'assets': {},
    "sequence": -100,
    'license': 'LGPL-3',
    'application': True,
    'installable': True,
    'auto_install': False,
}
