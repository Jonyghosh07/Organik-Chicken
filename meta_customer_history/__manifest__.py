{
    'name': "Customer Order History",
    'summary': """
        Create customer Order history in contact list view....""",
    'description': """
        Custom Customer fields....
        Create customer Order history in contact list view
            """,
    'author': 'Metamorphosis',
    'co-author': "Jony Ghosh",
    'company': 'Metamorphosis',
    'category': 'Tools',
    'version': '16.0.2.0.0',
    'depends': ['contacts', 'base', 'meta_delivery_portal', 'account_followup'],
    'data': [
            "views/res_partner_view.xml",
    ],
    'license': 'LGPL-3',
    'installable': True,
    'auto_install': False,
    'application': True,
}