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


class AccountPaymentGroup(models.Model):
    _inherit = "account.payment.group"


    @api.multi
    def compute_withholdings(self):
        self.set_currency_rate()
        self.control_currency()
        for line in self.payment_ids:
            line.currency_id = self.currency_id.id
        res = super(AccountPaymentGroup, self).compute_withholdings()
        self.change_currency_payments()
        return res