from odoo import models, fields, api, _

class AccountInvoice(models.Model):
    _inherit = "account.invoice"

    manual_currency_rate_visible = fields.Boolean('Manual Currency Rate Visible')

    @api.onchange('currency_id')
    def onchange_currency_id(self):
        if self.currency_id:
            visible = True
            company_currency_id = self.env.user.company_id.currency_id.id
            if company_currency_id == self.currency_id.id:
                visible = False
            self.manual_currency_rate_visible = visible
