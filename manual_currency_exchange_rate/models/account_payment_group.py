##############################################################################
# For copyright and license notices, see __manifest__.py file in module root
# directory
##############################################################################
from odoo import models, fields, api, _
import odoo.addons.decimal_precision as dp
from odoo.exceptions import UserError, ValidationError
from ast import literal_eval
from odoo.tools.safe_eval import safe_eval as eval
from dateutil.relativedelta import relativedelta
import datetime

### este modifico Matias y cada metodo arriba aclara que hizo..
class AccountPaymentGroup(models.Model):
    _inherit = "account.payment.group"

    ### Fields
    payment_currency_id = fields.Many2one('res.currency', string="Payment Currency")
    payment_currency_rate = fields.Float(string='Payment Currency Rate',  )
    #payment_difference_currency = fields.Float(string='Payment Difference Currency',  )
    ### end


    # solo llama a los metodos de abajo
    @api.multi
    def post(self):
        self.set_currency_rate()
        self.control_currency()
        #self.payments_line_same_currency()
        return super(AccountPaymentGroup, self).post()

    # control de que todas las lineas de pagos tengan la misma currency
    @api.multi
    def payments_line_same_currency(self):
        aux_currency_id = None
        for line in self.payment_ids:
            if not aux_currency_id:
                aux_currency_id = line.currency_id.id
            else:
                if aux_currency_id != line.currency_id.id:
                    raise UserError(_('You cannot have Payments in different Currency.'))
        if aux_currency_id != self.payment_currency_id.id:
            raise UserError(_('You cannot have Payments in different Payment Group Currency.'))

    # cambia si tiene alguna otra moneda y hace el "traspaso" del monto de lo que tenga a la moneda del pago
    @api.multi
    def change_currency_payments(self):
        for line in self.payment_ids:
            if self.payment_currency_id and line.currency_id.id != self.payment_currency_id.id:
                currency_id = line.currency_id.with_context(date=self.payment_date) # para usar el valor del dolar del pago
                line.withholding_base_amount = currency_id.compute(line.withholding_base_amount, self.payment_currency_id)
                line.amount = currency_id.compute(line.amount, self.payment_currency_id)
                line.currency_id = self.payment_currency_id.id
        
    @api.multi
    def control_currency(self):
        aux_currency_id = None
        ### se comenta por que es necesario poder validar con 2 monedas en las lineas a pagar.-
        # for line2pay in self.to_pay_move_line_ids:
        #     currency_compare = line2pay.currency_id
        #     if not line2pay.currency_id:
        #         currency_compare = line2pay.company_id.currency_id.id
        #     if not aux_currency_id:
        #         aux_currency_id = currency_compare
        #     else:
        #         if aux_currency_id != currency_compare:
        #             raise UserError(_('You cannot have debts/payments in different currency.'))


    @api.multi
    def compute_withholdings(self):
        self.set_currency_rate()
        self.control_currency()
        for line in self.payment_ids:
            line.currency_id = self.currency_id.id
        res = super(AccountPaymentGroup, self).compute_withholdings()
        self.change_currency_payments()
        return res


    # @api.onchange('payment_currency_rate') ?????????????????
    # def onchange_payment_currency_rate(self):
    #     self.set_currency_rate()

    @api.onchange('payment_date') 
    def onchange_payment_date(self):
        if self.payment_currency_id and self.payment_date:
            currency_rate_id = self.env['res.currency.rate'].search([
                                        ('currency_id', '=', self.payment_currency_id.id),
                                        ('name', 'ilike', self.payment_date)])
            if currency_rate_id:
                self.payment_currency_rate = currency_rate_id.inverse_rate

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
                'name': _("Manual Currency Rate"),
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
    def set_currency_rate(self):
        for rec in self.with_context({}):
            if rec.payment_currency_id and rec.payment_currency_id.id != rec.company_id.currency_id.id and rec.payment_currency_rate != 0.0:
                currency_rate_id = rec.env['res.currency.rate'].search([
                                ('currency_id', '=', rec.payment_currency_id.id),
                                ('name', 'ilike', rec.payment_date)])
                if currency_rate_id:
                    currency_rate_id.inverse_rate = rec.payment_currency_rate
                else:
                    rec.env['res.currency.rate'].create({'name': rec.payment_date, 
                                                          'inverse_rate': rec.payment_currency_rate,
                                                          'currency_id': rec.payment_currency_id.id})


    ## ESTE METODO CAMBIA LOS VALORES DEL GRUPO DE PAGO (LA CABECERA) SEGUN LAS FACTURAS/NOTAS CREDITOS QUE TENGA EN LAS LINEAS
    ## solo modifica las variables de la cabecera para que "esten bien"
    @api.multi
    @api.depends(
        'to_pay_move_line_ids.amount_residual',
        'to_pay_move_line_ids.amount_residual_currency',
        'to_pay_move_line_ids.currency_id',
        'to_pay_move_line_ids.invoice_id',
        'to_pay_move_line_ids',
        'payment_currency_id',
        'payment_date',
        'currency_id',
    )
    def _compute_selected_debt(self):
        for rec in self:
            rec.set_currency_rate()
            selected_finacial_debt = 0.0
            selected_debt = 0.0
            selected_debt_untaxed = 0.0
            for line in rec.to_pay_move_line_ids:
                if rec.payment_currency_id and  rec.payment_currency_id.id != rec.company_id.currency_id.id:
                    currency_id = line.currency_id.with_context(date=rec.payment_date)
                    selected_finacial_debt += line.financial_amount_residual
                    amount2use = line.amount_residual
                    if line.amount_residual_currency != 0.0:
                        amount2use = line.amount_residual_currency
                    # factor for total_untaxed
                    invoice = line.invoice_id
                    factor = invoice and invoice._get_tax_factor() or 1.0
                    selected_debt +=  currency_id.compute(amount2use, rec.currency_id) 
                    selected_debt_untaxed += currency_id.compute(amount2use, rec.currency_id)  * factor
                else:
                    selected_finacial_debt += line.financial_amount_residual
                    selected_debt += line.amount_residual
                    # factor for total_untaxed
                    invoice = line.invoice_id
                    factor = invoice and invoice._get_tax_factor() or 1.0
                    selected_debt_untaxed += line.amount_residual * factor
              
            sign = rec.partner_type == 'supplier' and -1.0 or 1.0
            rec.selected_finacial_debt = selected_finacial_debt * sign
            rec.selected_debt = selected_debt * sign
            rec.selected_debt_untaxed = selected_debt_untaxed * sign
    ## este es el metodo anterior copy and paste del modulo 
        #  addons-ingadhoc/account-payment/account_payment_group/models/account_payment_group.py:
    # def _compute_selected_debt(self):
    #     for rec in self:
    #         selected_finacial_debt = 0.0
    #         selected_debt = 0.0
    #         selected_debt_untaxed = 0.0
    #         for line in rec.to_pay_move_line_ids:
    #             selected_finacial_debt += line.financial_amount_residual
    #             selected_debt += line.amount_residual
    #             # factor for total_untaxed
    #             invoice = line.invoice_id
    #             factor = invoice and invoice._get_tax_factor() or 1.0
    #             selected_debt_untaxed += line.amount_residual * factor
    #         sign = rec.partner_type == 'supplier' and -1.0 or 1.0
    #         rec.selected_finacial_debt = selected_finacial_debt * sign
    #         rec.selected_debt = selected_debt * sign
    #         rec.selected_debt_untaxed = selected_debt_untaxed * sign




    @api.multi
    @api.depends('payment_ids.amount')
    def _compute_payments_amount(self):
        for rec in self:
            amount = 0.0
            for line in rec.payment_ids:
                currency_id = line.currency_id.with_context(date=rec.payment_date) # para usar el valor del dolar del pago
                amount += currency_id.compute(line.amount, rec.currency_id)
            
            rec.payments_amount = amount
