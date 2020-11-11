##############################################################################
# For copyright and license notices, see __manifest__.py file in module root
# directory
##############################################################################
from odoo import fields, api, models


class ManualCurrencyRate(models.TransientModel):
    _name = 'manual.currency.rate'
    _description = "Manual Currency Rate"

    
    bna_rate_uds_sale = fields.Float('BNA USD Sale', readonly=True, )
    bna_rate_uds_purchase = fields.Float('BNA USD Purchase', readonly=True, )
    afip_pyafipws_currency_rate = fields.Float('AFIP', readonly=True, )
    last_rate = fields.Float('Last rate in day', readonly=True, )
    manual_rate = fields.Float('Manual Rate',)


    def set_bna_sale(self):
        self.set_rate(self.bna_rate_uds_sale)

    def set_bna_purchase(self):
        self.set_rate(self.bna_rate_uds_purchase)

    def set_afip(self):
        self.set_rate(self.afip_pyafipws_currency_rate)

    def set_last(self):
        self.set_rate(self.last_rate)

    def set_manual(self):
        self.set_rate(self.manual_rate)

    def set_rate(self, rate):
        if self._context['active_model'] == 'account.invoice':
            invoice = self.env['account.invoice'].browse(self._context['active_id'])
            if invoice.currency_id:
                currency_date = invoice.date if invoice.date else invoice.date_invoice
                invoice.currency_rate = rate
                currency_rate_id = self.env['res.currency.rate'].search([('currency_id', '=', invoice.currency_id.id), \
                    ('name', 'ilike', currency_date)])
                if currency_rate_id:
                    currency_rate_id.inverse_rate = rate
                else:
                    self.env['res.currency.rate'].create({'name': currency_date, 'inverse_rate': rate, 'currency_id': invoice.currency_id.id})

        if self._context['active_model'] == 'account.payment':
            payment = self.env['account.payment'].browse(self._context['active_id'])
            if payment.currency_id:
                currency_date = payment.payment_date
                payment.exchange_rate = rate
                currency_rate_id = self.env['res.currency.rate'].search([('currency_id', '=', payment.currency_id.id), \
                    ('name', 'ilike', currency_date)])
                if currency_rate_id:
                    currency_rate_id.inverse_rate = rate
                else:
                    self.env['res.currency.rate'].create({'name': currency_date, 'inverse_rate': rate, 'currency_id': payment.currency_id.id})

        if self._context['active_model'] == 'account.payment.group':
            payment_group = self.env['account.payment.group'].browse(self._context['active_id'])
            if payment_group.payment_currency_id :
                currency_date = payment_group.payment_date
                payment_group.payment_currency_rate = rate
                currency_rate_id = self.env['res.currency.rate'].search([('currency_id', '=', payment_group.payment_currency_id.id), \
                    ('name', 'ilike', currency_date)])
                if currency_rate_id:
                    currency_rate_id.inverse_rate = rate
                else:
                    self.env['res.currency.rate'].create({'name': currency_date, 'inverse_rate': rate, 'currency_id': payment_group.payment_currency_id.id})
            payment_group._compute_selected_debt()



