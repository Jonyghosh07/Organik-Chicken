{
    'name': 'Batch Details',
    'version': '16.1.1.5',
    'description': """Keep chicken details inside Lot/Serial Number.... """,
    'author': 'Metamorphosis',
    'co-author': "Jony Ghosh",
    'company': 'Metamorphosis',
    'website': 'https://www.metamorphosis.com.bd/',
    'summary': """ Keep chicken details inside Lot/Serial Number....  """,
    'category': 'Website',
    'data': [
            "views/auth_signup.xml",
            "views/batch_fields_view.xml",
            "views/web_sale_view.xml",
            "views/customer_area_view.xml",
            "views/sale_order_line_view.xml",
        ],
    'depends': [
        'base','stock','sale',
        'website_sale', 'meta_area_addition',
        'abs_so_minimum_quantity', 'auth_signup',
        'product'],
    'assets':{
        'web.assets_frontend':[
            '/meta_batch_order/static/src/js/sale_update.js',
        ]
    },
    "license": "Other proprietary",
    'installable': True,
    'auto_install': False,
    'application': False,
}