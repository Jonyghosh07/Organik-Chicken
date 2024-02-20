# -*- coding: utf-8 -*-

{
    'name': "Area, Sub Area fields addition",
    'summary': 'Add area, locality fields',
    'description': "Additional fields in contacts",
    'version': '1.0',
    'depends': [
        'contacts',
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/custom_views.xml',
        'views/delivery_hub.xml',
    ],
    'license': 'LGPL-3',
    'application': True,
    'installable': True,
    'auto_install': False,
}
