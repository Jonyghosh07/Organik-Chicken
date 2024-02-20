{
    'name': "OTP",
    'summary': """
        Create OTP """,
    'description': """
        OTP generate
            """,
    'author': 'Metamorphosis',
    'co-author': "Jony Ghosh",
    'company': 'Metamorphosis',
    'category': 'Tools',
    'version': '16.0.2.0.0',
    'depends': ['contacts', 'base', 'sale_management', 'meta_sms_mod'],
    'data': [
            'security/ir.model.access.csv',
            'views/res_partner.xml',
    ],
    'license': 'LGPL-3',
    'installable': True,
    'auto_install': False,
    'application': True,
}