##############################################################################
# For copyright and license notices, see __manifest__.py file in module root
# directory
##############################################################################
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from dateutil.relativedelta import relativedelta
import requests
import sys
from lxml import html

import re
import logging
_logger = logging.getLogger(__name__)

class AccountInvoice(models.Model):
    _inherit = "account.invoice"


    @api.multi
    def action_invoice_open(self):
        aux = (self.currency_rate)
        res = super(AccountInvoice, self).action_invoice_open()
        if aux != 0.0:
            self.currency_rate = aux
        return res


    def set_rate(self):
        if self.currency_id and self.date_invoice:
            # currency_date = self.date_invoice
            # currency_rate_id = self.env['res.currency.rate'].search([('currency_id', '=', self.currency_id.id), \
            #     ('name', 'ilike', currency_date)])
            # bna_rate_uds_purchase, bna_rate_uds_sale, afip_pyafipws_currency_rate, last_rate= 0.0, 0.0, 0.0, 0.0
            # url = "http://www.bna.com.ar/Cotizador/MonedasHistorico"
            # page = self.download(url)
            # if page:
            #     tree = html.fromstring(page.content)
            #     xpath_string = '//table/tbody/tr[1]/td[2]'
            #     results = tree.xpath(xpath_string)
            #     bna_rate_uds_purchase = results[0].text
            #     xpath_string = '//table/tbody/tr[1]/td[3]'
            #     results = tree.xpath(xpath_string)
            #     bna_rate_uds_sale = results[0].text
            # afip_pyafipws_currency_rate = self.currency_id.get_pyafipws_currency_rate()[0]
            # if currency_rate_id:
            #     last_rate = currency_rate_id.inverse_rate
                
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


    def download(self, url):
        r = requests.get(url)
        if r.status_code != 200:
            sys.stderr.write("! Error {} retrieving url {}\n".format(r.status_code, url))
            return None
        return r