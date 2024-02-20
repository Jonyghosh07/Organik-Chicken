# -*- coding: utf-8 -*-

{
    "name":  "Website OTP Authentication",
    "summary":  """Odoo Website OTP Authentication makes secure environment in your odoo website for your portal users.""",
    "category":  "Website",
    "version":  "16.1.1",
    "sequence":  1,
    "author":  "Webkul Software Pvt. Ltd.",
    "co-author": "Jony Ghosh",
    "license":  "Other proprietary",
    "website":  "https://metamorphosis.com.bd/",
    "description":  """OTP
                    One Time Authentication Password
                    OTP Authentication
                    Website OTP Authentication
                    Odoo Website OTP Authentication
                    One Time Password
                    One Time Password Authentication
                    Access Management
                    SMS OTP
                    SMS One Time Password
                    Odoo OTP SMS Notification
                    Login via OTP
                    Login via OTP Authentication
                    Odoo
                    Website""",
    "depends":  ['web', 'website', 'portal', 'auth_signup'],
    "data":  [
        'security/ir.model.access.csv',
        'views/auth_signup_login_templates.xml',
        'views/webclient_templates.xml',
        'edi/otp_edi_template.xml',
        'views/res_config_views.xml',
        'views/res_user_view.xml',
        'data/data_otp.xml',
    ],

    'assets': {
        'web.assets_frontend': [
            'otp_auth/static/src/**/*.scss',
            'otp_auth/static/src/**/*.js',
        ],
    },

    "images":  ['static/description/Banner.png'],
    "application":  True,
    "installable":  True,
    "auto_install":  False,
    "price":  35,
    "currency":  "USD",
    "pre_init_hook":  "pre_init_check",
}
