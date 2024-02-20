# -*- coding: utf-8 -*-
{
    'name': "Barcode Print Custom Format",

    'summary': """
        Print Product barcode in custom page format of 25mm x 50mm page.
        """,

    'description': """
        Print Product barcode in custom page format of 25mm x 50mm page.
    """,

    'author': "Md. Niaj Shahriar Shishir",
    'website': "https://metamorphosis.com.bd",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/13.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Inventory',
    'version': '13.0.0.1',

    # any module necessary for this one to work correctly
    'depends': ['stock_barcode'],

    # always loaded
    'data': [

        # 'report/report_picking_operations.xml',
        'report/report_product_barcode_pdf.xml',
        'data/paper_format.xml'
    ],
    'license':'AGPL-3',    
    'installable': True,
    'auto_install': False,
    'application': True,
}
