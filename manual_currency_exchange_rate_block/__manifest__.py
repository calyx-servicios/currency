# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    "name": "Manual Currency Exchange Rate Block",
    "summary": """
        Block button to change currency exchange when the selected currency is de same as the current company
    """,
    "author": "Calyx Servicios S.A.",
    "maintainers": ["gpperez"],
    "website": "https://odoo.calyx-cloud.com.ar/",
    "license": "AGPL-3",
    "category": "Tools",
    "version": "11.0.1.0.0",
    "development_status": "Production/Stable",
    "application": False,
    "installable": True,
    "depends": ['manual_currency_exchange_rate'],
    'data': [
        'views/account_invoice_view.xml',
    ],
}
