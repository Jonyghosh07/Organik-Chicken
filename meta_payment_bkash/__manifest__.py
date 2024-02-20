{
    'name': 'bKash Payment Gateway',
    'version': '16.0.1.0.0',
    'category': 'Accounting/Payment',
    'summary': 'Let your customers pay via bKash Payment Gateway directly from your website/portal',
    'description': 'bKash Payment Gateway Integration for Odoo 16. This module adds bKash as a payment provider that '
                   'lets your customer pay invoice and sale order directly from odoo website and portal.',
    'author': 'Jony Ghosh',
    'company': 'Metamorphosis Limited',
    'maintainer': 'Metamorphosis Limited',
    'website': 'https://metamorphosis.com.bd',
    'depends': ['payment'],
    'data': [
        'views/views.xml',
        'views/templates.xml',
        'data/data.xml',
    ],
    'application': False,
    'post_init_hook': 'post_init_hook',
    'uninstall_hook': 'uninstall_hook',
    'license': 'AGPL-3'
}



