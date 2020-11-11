# -*- coding: utf-8 -*-
{
    'name': "Bank Extension",

    'summary': """
        Modificaciones y adaptaciones sobre modelos de cuentas bancarias y bancos""",

    'description': """
        
    """,

    'author': "Calyx",
    'website': "http://www.calyxservicios.com.ar",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Tools',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','manual_currency_exchange_rate'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        # 'views/res_partner_bank_view.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
    ],
}