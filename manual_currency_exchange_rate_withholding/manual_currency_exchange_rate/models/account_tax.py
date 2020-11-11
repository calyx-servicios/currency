from odoo import models, fields, api, _
import odoo.addons.decimal_precision as dp
from odoo.exceptions import UserError, ValidationError
from ast import literal_eval
from odoo.tools.safe_eval import safe_eval as eval
from dateutil.relativedelta import relativedelta
import datetime

# esto lo modifico matias
class AccountTax(models.Model):
    _inherit = "account.tax"

    # solo se cambia  el calculo dela fecha por que tiraba error.. esta comentado bien en el medio
    ### EL METODO SI NO TIRA ERROR EN EL SERVER SE PODRIA SACAR
    @api.multi
    def get_period_payments_domain(self, payment_group):
        """
        We make this here so it can be inherited by localizations
        """
        to_date = fields.Date.from_string(
            payment_group.payment_date) or datetime.date.today()
        common_previous_domain = [
            ('partner_id.commercial_partner_id', '=',
                payment_group.commercial_partner_id.id),
        ]

## esto se agrega por que estaba dando error al usar las fechas..
        from_relative_delta = None
        from_date = None
        if self.withholding_accumulated_payments == 'month':
            from_relative_delta = relativedelta(day=1)
        elif self.withholding_accumulated_payments == 'year':
            from_relative_delta = relativedelta(day=1, month=1)
        if from_relative_delta:
            from_date = to_date + from_relative_delta
        else:
            from_date = to_date
## no se por que pero estaba 
    #     if self.withholding_accumulated_payments == 'month':
    #         from_relative_delta = relativedelta(day=1)
    #     elif self.withholding_accumulated_payments == 'year':
    #         from_relative_delta = relativedelta(day=1, month=1)
    #     from_date = to_date + from_relative_delta
## NO SE POR QUE ESTABA ESTO DE ARRIBA PERO "ANDABA" Y AHORA NO
        common_previous_domain += [
            ('payment_date', '<=', to_date),
            ('payment_date', '>=', from_date),
        ]
        previous_payment_groups_domain = common_previous_domain + [
            ('state', 'not in', ['draft', 'cancel', 'confirmed']),
            ('id', '!=', payment_group.id),
        ]
        # for compatibility with public_budget we check state not in and not
        # state in posted. Just in case someone implements payments cancelled
        # on posted payment group, we remove the cancel payments (not the
        # draft ones as they are also considered by public_budget)
        previous_payments_domain = common_previous_domain + [
            ('payment_group_id.state', 'not in',
                ['draft', 'cancel', 'confirmed']),
            ('state', '!=', 'cancel'),
            ('tax_withholding_id', '=', self.id),
            ('payment_group_id.id', '!=', payment_group.id),
        ]
        return (previous_payment_groups_domain, previous_payments_domain)

    ## ESTE METODO DE ABAJO "TRAE" todos los valores de la retencion..
    ## lo unico que se hace es extender lo q trae y agregarle un "calculo nuevo" a previous_withholding_amount que es las retenciones previas
    # esto tiraba error cuando estaabn las retenciones en dolares y tenia que suamar el total en pesos..
    @api.multi
    def get_withholding_vals(self, payment_group, force_withholding_amount_type=None):
        result = super(AccountTax, self).get_withholding_vals(payment_group,force_withholding_amount_type=force_withholding_amount_type)
        previous_withholding_amount = 0.0
        previos_payment_groups_domain, previos_payments_domain = (self.get_period_payments_domain(payment_group))
        for payment_obj in self.env['account.payment'].search(previos_payments_domain):
            currency_id = payment_obj.currency_id.with_context(date=payment_obj.payment_group_id.payment_date) # para usar el valor del dolar del pago
            previous_withholding_amount += currency_id.compute(payment_obj.amount, payment_group.currency_id)
        result['previous_withholding_amount']   = previous_withholding_amount  
        return result

        # """
        # If you wan to inherit and implement your own type, the most important
        # value tu return are period_withholding_amount and
        # previous_withholding_amount, with thos values the withholding amount
        # will be calculated.
        # """
        # self.ensure_one()
        # withholding_amount_type = force_withholding_amount_type or \
        #     self.withholding_amount_type
        # if withholding_amount_type == 'untaxed_amount':
        #     withholdable_invoiced_amount = payment_group.selected_debt_untaxed
        # else:
        #     withholdable_invoiced_amount = payment_group.selected_debt
        # withholdable_advanced_amount = 0.0
        # # if the unreconciled_amount is negative, then the user wants to make
        # # a partial payment. To get the right untaxed amount we need to know
        # # which invoice is going to be paid, we only allow partial payment
        # # on last invoice
        # if payment_group.withholdable_advanced_amount < 0.0 and \
        #         payment_group.to_pay_move_line_ids:
        #     withholdable_advanced_amount = 0.0

        #     sign = payment_group.partner_type == 'supplier' and -1.0 or 1.0
        #     sorted_to_pay_lines = sorted(
        #         payment_group.to_pay_move_line_ids,
        #         key=lambda a: a.date_maturity or a.date)

        #     # last line to be reconciled
        #     partial_line = sorted_to_pay_lines[-1]
        #     if sign * partial_line.amount_residual < \
        #             sign * payment_group.withholdable_advanced_amount:
        #         raise ValidationError(_(
        #             'Seleccionó deuda por %s pero aparentente desea pagar '
        #             ' %s. En la deuda seleccionada hay algunos comprobantes de'
        #             ' mas que no van a poder ser pagados (%s). Deberá quitar '
        #             ' dichos comprobantes de la deuda seleccionada para poder '
        #             'hacer el correcto cálculo de las retenciones.' % (
        #                 payment_group.selected_debt,
        #                 payment_group.to_pay_amount,
        #                 partial_line.move_id.display_name,
        #                 )))

        #     if withholding_amount_type == 'untaxed_amount' and \
        #             partial_line.invoice_id:
        #         invoice_factor = partial_line.invoice_id._get_tax_factor()
        #     else:
        #         invoice_factor = 1.0

        #     # le descontamos de la base imponible el saldo que no se esta
        #     # pagando descontado de iva
        #     withholdable_invoiced_amount -= (
        #         sign * payment_group.withholdable_advanced_amount
        #         * invoice_factor)
        # elif self.withholding_advances:
        #     withholdable_advanced_amount = \
        #         payment_group.withholdable_advanced_amount

        # accumulated_amount = previous_withholding_amount = 0.0

        # if self.withholding_accumulated_payments:
        #     previos_payment_groups_domain, previos_payments_domain = (
        #         self.get_period_payments_domain(payment_group))
        #     same_period_payments = self.env['account.payment.group'].search(
        #         previos_payment_groups_domain)
        #     for same_period_payment_group in same_period_payments:
        #         # obtenemos importe acumulado sujeto a retencion de pagos
        #         # anteriores. Por compatibilidad con public_budget aceptamos
        #         # pagos en otros estados no validados donde el matched y
        #         # unmatched no se computaron, por eso agragamos la condición
        #         if same_period_payment_group.state == 'posted':
        #             accumulated_amount += (
        #                 same_period_payment_group.matched_amount)
        #             if self.withholding_advances:
        #                 accumulated_amount += (
        #                     same_period_payment_group.unmatched_amount)
        #         else:
        #             accumulated_amount += (
        #                 same_period_payment_group.to_pay_amount)
        #             if self.withholding_advances:
        #                 accumulated_amount += (
        #                     same_period_payment_group.unreconciled_amount)
        #     previous_withholding_amount = sum(
        #         self.env['account.payment'].search(
        #             previos_payments_domain).mapped('amount'))

        # total_amount = (
        #     accumulated_amount +
        #     withholdable_advanced_amount +
        #     withholdable_invoiced_amount)
        # withholding_non_taxable_minimum = self.withholding_non_taxable_minimum
        # withholding_non_taxable_amount = self.withholding_non_taxable_amount
        # withholdable_base_amount = (
        #     (total_amount > withholding_non_taxable_minimum) and
        #     (total_amount - withholding_non_taxable_amount) or 0.0)

        # comment = False
        # if self.withholding_type == 'code':
        #     localdict = {
        #         'withholdable_base_amount': withholdable_base_amount,
        #         'payment': payment_group,
        #         'partner': payment_group.commercial_partner_id,
        #         'withholding_tax': self,
        #     }
        #     eval(
        #         self.withholding_python_compute, localdict,
        #         mode="exec", nocopy=True)
        #     period_withholding_amount = localdict['result']
        # else:
        #     rule = self._get_rule(payment_group)
        #     percentage = 0.0
        #     fix_amount = 0.0
        #     if rule:
        #         percentage = rule.percentage
        #         fix_amount = rule.fix_amount
        #         comment = '%s x %s + %s' % (
        #             withholdable_base_amount,
        #             percentage,
        #             fix_amount)

        #     period_withholding_amount = (
        #         (total_amount > withholding_non_taxable_minimum) and (
        #             withholdable_base_amount * percentage + fix_amount) or 0.0)

        # return {
        #     'withholdable_invoiced_amount': withholdable_invoiced_amount,
        #     'withholdable_advanced_amount': withholdable_advanced_amount,
        #     'accumulated_amount': accumulated_amount,
        #     'total_amount': total_amount,
        #     'withholding_non_taxable_minimum': withholding_non_taxable_minimum,
        #     'withholding_non_taxable_amount': withholding_non_taxable_amount,
        #     'withholdable_base_amount': withholdable_base_amount,
        #     'period_withholding_amount': period_withholding_amount,
        #     'previous_withholding_amount': previous_withholding_amount,
        #     'payment_group_id': payment_group.id,
        #     'tax_withholding_id': self.id,
        #     'automatic': True,
        #     'comment': comment,
        # }

