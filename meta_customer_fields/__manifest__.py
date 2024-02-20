{
    'name': "Customer Fields",
    'summary': """
        Create customer custom fields (Facebook ID, WhatsApp Number, Bkash Number, Nagad Number, Is Delivery Man,
        Is Subscriber, subscription_line, map_url, Customer Type, Remarks). Also Creates Delivery Man field 
        in Sale Order.. And new model Subscription line....""",
    'description': """
        Custom Customer fields....
        The fields is added, are : Facebook ID, WhatsApp Number, Bkash Number, Nagad Number, Is Delivery Man,
        Is Subscriber, subscription_line, map_url, Customer Type, Remarks..
        Also Creates Delivery Man field in Sale Order. 
        A new model Subscription line.
            """,
    'author': 'Metamorphosis',
    'co-author': "Jony Ghosh",
    'company': 'Metamorphosis',
    'category': 'Tools',
    'version': '16.0.2.0.0',
    'depends': ['contacts', 'base', 'sale_management', 'meta_batch_order'],
    'data': [
        'security/ir.model.access.csv',
        'views/res_contact_view.xml',
        'views/sale_order_view.xml',
    ],
    'license': 'LGPL-3',
    'installable': True,
    'auto_install': False,
    'application': True,
}