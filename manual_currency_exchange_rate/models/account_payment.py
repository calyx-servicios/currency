##############################################################################
# For copyright and license notices, see __manifest__.py file in module root
# directory
##############################################################################
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from dateutil.relativedelta import relativedelta
import re
import logging
_logger = logging.getLogger(__name__)
import requests
import sys
from lxml import html

### este es del base q habia echo mario no lo use nunca..
class AccountPayment(models.Model):
    _inherit = "account.payment"

    @api.model 
    def create(self, vals):
        self = super(AccountPayment, self).create(vals)
        if self.currency_id:
            currency_date = self.payment_date
            currency_rate_id = self.env['res.currency.rate'].search([('currency_id', '=', self.currency_id.id), \
                ('name', 'ilike', currency_date)])
            if currency_rate_id:
                currency_rate_id.inverse_rate = self.exchange_rate
            else:
                if self.currency_id.id != self.company_id.currency_id.id and self.exchange_rate != 0.0:
                    self.env['res.currency.rate'].create({'name': currency_date, 'inverse_rate': self.exchange_rate, \
                        'currency_id': self.currency_id.id})
        return self

    @api.onchange('exchange_rate')
    def onchange_exchange_rate(self):
        self.amount_company_currency = self.amount * self.exchange_rate



    @api.onchange('currency_id')
    def onchange_currency_id_amount(self):
        if self.currency_id and self.currency_id.id != self.payment_group_id.company_id.currency_id.id:
            currency_id = self.payment_group_id.company_id.currency_id.with_context(date=self.payment_group_id.payment_date) # para usar el valor del dolar del pago
            self.amount = currency_id.compute(self.payment_group_id.payment_difference, self.currency_id)
        

    @api.multi
    def get_amount_currency(self,amount_return):
        # self.payment_group_id.amount_company_currency
        # currency_id = self.currency_id.with_context(date=self.payment_date) #para usar el valor del dolar de la factura        
        # amount_return = currency_id.compute(amount_return, self.company_id.currency_id)
        return self.amount_company_currency

    def set_rate(self):
        if self.currency_id and self.payment_date:
        #     currency_date = self.payment_date
        #     currency_rate_id = self.env['res.currency.rate'].search([('currency_id', '=', self.currency_id.id), \
        #         ('name', 'ilike', currency_date)])
        #     bna_rate_uds_purchase, bna_rate_uds_sale, afip_pyafipws_currency_rate, last_rate= 0.0, 0.0, 0.0, 0.0
        #     url = "http://www.bna.com.ar/Cotizador/MonedasHistorico"
        #     page = requests.get(url)
        #     if page.status_code != 200:
        #         sys.stderr.write("! Error {} retrieving url {}\n".format(page.status_code, url))

        #     if page:
        #         tree = html.fromstring(page.content)
        #         xpath_string = '//table/tbody/tr[1]/td[2]'
        #         results = tree.xpath(xpath_string)
        #         bna_rate_uds_purchase = results[0].text
        #         xpath_string = '//table/tbody/tr[1]/td[3]'
        #         results = tree.xpath(xpath_string)
        #         bna_rate_uds_sale = results[0].text
        #     afip_pyafipws_currency_rate = self.currency_id.get_pyafipws_currency_rate()[0]
        #     if currency_rate_id:
        #         last_rate = currency_rate_id.inverse_rate
                
            return {    
                'name': _("Manua Currency Rate"),
                'type': 'ir.actions.act_window',
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'manual.currency.rate',
                'target': 'new',
                # 'context': {'default_bna_rate_uds_sale': bna_rate_uds_sale, 
                #             'default_bna_rate_uds_purchase': bna_rate_uds_purchase,
                #             'default_afip_pyafipws_currency_rate': afip_pyafipws_currency_rate,
                #             'default_last_rate': last_rate,
                #             }
            }


    @api.multi
    @api.constrains('payment_group_id', 'payment_type')
    def check_payment_group(self):
        # odoo tests don't create payments with payment gorups
        if self.env.registry.in_test_mode():
            return True
        # for rec in self:
        #     if rec.partner_type and rec.partner_id and \
        #        not rec.payment_group_id:
        #         raise ValidationError(_(
        #             'Payments with partners must be created from '
        #             'payments groups'))
        #     # transfers or payments from bank reconciliation without partners
        #     elif not rec.partner_type and rec.payment_group_id:
        #         raise ValidationError(_(
        #             "Payments without partners (usually transfers) cant't "
        #             "have a related payment group"))