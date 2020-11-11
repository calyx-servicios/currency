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
class AccountBankStatement(models.Model):
    _inherit = "account.bank.statement"

    currency_rate = fields.Float(
        string='Currency Rate',
        copy=False,
        digits=(16, 4),
        readonly=False,
    )

    def set_rate(self, rate):
        if self.currency_rate:
            for line in self.line_ids:
                line.currency_rate = self.currency_rate


    def write(self, vals):
        super(AccountBankStatement, self).write(vals)
        for statement in self:
            for line in statement.line_ids:
                currency_date = line.date
                currency_rate_id = statement.env['res.currency.rate'].search([('currency_id', '=', statement.currency_id.id), \
                    ('name', 'ilike', currency_date)])
                if currency_rate_id:
                    currency_rate_id.inverse_rate = line.currency_rate
                else:
                    statement.env['res.currency.rate'].create({'name': currency_date, 'inverse_rate': line.currency_rate, 'currency_id': self.currency_id.id})


class AccountBankStatementLine(models.Model):
    _inherit = "account.bank.statement.line"

    currency_rate = fields.Float(
        string='Currency Rate',
        copy=False,
        digits=(16, 4),
        readonly=False,
    )