# -*- coding: utf-8 -*-
{
    'name': "Manual Currency Exchange Rate",

    'summary': """
         """,

    'description': """
        Manual Currency Exchange Rate
    """,

    'author': "Calyx",
    'website': "http://www.calyxservicios.com.ar",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Tools',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'account', 'sale', 'account_payment_group', 'base_currency_inverse_rate', 'l10n_ar_account'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'wizards/manual_currency_rate_views.xml',
        #'views/account_payment_view.xml',
        'views/account_payment_group_view.xml',
        'views/account_invoice_view.xml',
        'views/accoun_bank_statement_view.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
    ],
}